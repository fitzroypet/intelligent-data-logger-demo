"""Bounded model orchestration over restricted diagnostic evidence, not raw data."""
from __future__ import annotations

import json
import time

from src.research.policy import diagnose

PROMPT = """You are the interface for a synthetic solar-system research experiment.
Use the appropriate evidence tool before making factual claims. You receive no raw telemetry.
After the tool result, return only a JSON object with keys label, explanation, citations.
label must faithfully reflect the evidence tool's label, including unknown when it abstains.
citations must be a list of measurement names actually present in the tool receipt.
Do not infer customer responsibility, warranties, intent or real-world accuracy.
Do not invent measurements or perform your own engineering calculations.
If the tool abstains, explain the missing evidence. All observations are synthetic.
"""
QUESTIONS = {
    "daily_output": "What explains the solar output on {day}? Is there a material reduction?",
    "alarm": "Investigate any inverter alarm on {day}. What explanation is supported?",
    "pv_trend": "Has PV performance declined over the stored history up to {day}?",
}
TOOLS = [{"name": task, "description": description,
          "input_schema": {"type":"object", "properties":{}, "additionalProperties":False}}
         for task, description in [
             ("daily_output", "Assess one day's solar output against the evidence available."),
             ("alarm", "Assess inverter alarms and their supported technical explanation."),
             ("pv_trend", "Assess longitudinal PV performance change with available history.")]]


def score_final(text, receipt, expected):
    result = {"valid_json": False, "label_fidelity": False, "oracle_correct": False,
              "citation_validity": False, "nonempty_explanation": False}
    try:
        parsed = json.loads(text)
        if not isinstance(parsed, dict): return result
        result["valid_json"] = True
        result["label_fidelity"] = parsed.get("label") == receipt["label"]
        result["oracle_correct"] = parsed.get("label") == expected
        names = parsed.get("citations")
        result["citation_validity"] = (isinstance(names,list) and all(isinstance(n,str) for n in names)
            and bool(names) and set(names).issubset(receipt["measurements"]))
        result["nonempty_explanation"] = isinstance(parsed.get("explanation"),str) and bool(parsed["explanation"].strip())
    except (ValueError, TypeError):
        pass
    return result


class Budget:
    """Reserve conservative serialized-byte token bounds before every request."""
    def __init__(self, config, max_usd=3.0):
        self.config=config; self.max_usd=max_usd; self.requests=0; self.reserved_usd=0.0; self.actual_estimate=0.0

    def reserve(self, kwargs):
        # Conservative planning approximation, not an Anthropic billing guarantee.
        input_bound = len(json.dumps(kwargs, ensure_ascii=False).encode("utf-8"))+2000
        amount = (input_bound*self.config["input_usd_per_million"] +
                  kwargs["max_tokens"]*self.config["output_usd_per_million"])/1e6
        if self.requests >= self.config["max_requests"] or self.reserved_usd+amount > self.max_usd:
            raise RuntimeError("Local request/cost reservation limit reached")
        self.requests+=1; self.reserved_usd+=amount

    def record(self, usage):
        self.actual_estimate += (usage.get("input_tokens",0)*self.config["input_usd_per_million"]+
                                 usage.get("output_tokens",0)*self.config["output_usd_per_million"])/1e6


def run_case(client, view, static, task, expected, thresholds, config, budget):
    start=time.perf_counter()
    question=QUESTIONS[task].format(day=str(view.timestamp.max().date()))
    record={"question":question,"system_prompt":PROMPT,"tools_schema":TOOLS,"responses":[],
            "tool_receipts":[],"status":"error","tool_selection_correct":False}
    messages=[{"role":"user","content":question}]
    def request(tool_choice):
        kwargs=dict(model=config["model"],max_tokens=config["max_output_tokens"],temperature=0,
                    system=PROMPT,tools=TOOLS,messages=messages,tool_choice=tool_choice)
        budget.reserve(kwargs)
        response=client.messages.create(**kwargs)
        usage=response.usage.model_dump()
        budget.record(usage)
        blocks=[b.model_dump() for b in response.content]
        record["responses"].append({"content":blocks,"usage":usage,"model":response.model,
                                    "stop_reason":response.stop_reason,"request_id":getattr(response,"_request_id",None)})
        return blocks
    try:
        blocks=request({"type":"any","disable_parallel_tool_use":True})
        messages.append({"role":"assistant","content":blocks})
        calls=[b for b in blocks if b["type"]=="tool_use"]
        if len(calls)!=1:
            record["status"]="invalid_tool_count"
        else:
            call=calls[0]
            correct=call["name"]==task and call["input"]=={}
            record["tool_selection_correct"]=correct
            if call["name"] not in QUESTIONS or call["input"]!={}:
                record["status"]="invalid_tool"
            else:
                receipt=diagnose(view,static,call["name"],thresholds)
                record["tool_receipts"].append({"tool":call["name"],"receipt":receipt})
                messages.append({"role":"user","content":[{"type":"tool_result","tool_use_id":call["id"],
                                 "content":json.dumps(receipt,allow_nan=False)}]})
                blocks=request({"type":"none"})
                text="\n".join(b["text"] for b in blocks if b["type"]=="text")
                record["final_text"]=text
                record["scores"]=score_final(text,receipt,expected)
                record["status"]="complete" if record["responses"][-1]["stop_reason"]=="end_turn" else "truncated"
    except Exception as exc:
        # Never serialize API error bodies that may contain secrets or account details.
        record["error_type"]=type(exc).__name__
        if isinstance(exc,RuntimeError) and str(exc)=="Local request/cost reservation limit reached":
            record["status"]="budget_limit"
    record["messages"]=messages
    record["elapsed_seconds"]=round(time.perf_counter()-start,3)
    return record
