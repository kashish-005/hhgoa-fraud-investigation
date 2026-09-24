import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
import graph_tools

load_dotenv()

# The new SDK automatically picks up GEMINI_API_KEY from the environment
client = genai.Client()

SYSTEM_INSTRUCTION = """You are a fraud investigation agent for a bank. You investigate flagged
transactions using graph evidence and decide the next best action.

Your process, every time:
1. Gather evidence using the available tools — transaction history, connected entities
   (device/email/region), and prior closed cases on the same card.
2. Identify the likely fraud pattern (or conclude the activity looks legitimate).
3. Assess your confidence/risk level given the evidence.
4. If evidence is insufficient to act defensibly, say so explicitly and name what
   additional evidence would help.
5. Recommend one or more next actions from: allow, block_transaction, block_account,
   monitor_account, warn_customer, escalate_to_analyst, file_report (SAR).
   Note whether each action requires human approval.
6. When you have reached a decision, respond with a final JSON object (and nothing else)
   in this exact shape:
   {
     "case_id": "...",
     "pattern": "...",
     "risk_level": "low|medium|high",
     "confidence": "low|medium|high",
     "evidence_summary": "...",
     "reasoning": "...",
     "recommended_actions": [{"action": "...", "requires_approval": true|false}],
     "sar_required": true|false,
     "explanation": "..."
   }

risk_score is an input signal from the bank's model, not a verdict — treat it as one
piece of evidence among several, not as ground truth.
"""

def run_investigation(case: dict) -> dict:
    opening_prompt = f"""New fraud investigation triggered.

Case ID: {case['case_id']}
Trigger: {case.get('trigger_text', '')}
Flagged transaction: {case['flagged_txn_id']}
Customer: {case['customer_id']}
Card: {case['card_id']}
Risk score (input signal, not verdict): {case.get('risk_score')}

Investigate using your tools, then respond with the final JSON decision as instructed."""

    print("Starting investigation. Hitting tools...")
    
    chat = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[
                graph_tools.get_transaction_history,
                graph_tools.get_connected_entities,
                graph_tools.get_prior_cases
            ],
            temperature=0.1,
        )
    )

    response = chat.send_message(opening_prompt)
    
    try:
        final_text = response.text.strip()
        if final_text.startswith("```"):
            final_text = final_text.strip("`").lstrip("json").strip()
        return json.loads(final_text)
    except Exception as e:
        return {"error": "Could not parse final JSON", "raw": response.text}

if __name__ == "__main__":
    test_case = {
        "case_id": "HHG-001",
        "flagged_txn_id": "3514030",
        "customer_id": "C12382",
        "card_id": "C12382-K1",
        "risk_score": "0.61",
        "trigger_text": "Real-time model scored transaction 3514030 ($77.07, in billing region 444.0) at 0.61. Review and decide.",
    }

    result = run_investigation(test_case)
    print("\n=== FINAL DECISION ===")
    print(json.dumps(result, indent=2))