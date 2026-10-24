import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from luna.core.engine import LunaCEOEngine
from luna.core.state import LunaGlobalState
from luna.memory.database import memory_db

app = FastAPI(title="LUNA Executive Multi-Agent API", version="0.3.0")
engine = LunaCEOEngine()

STATIC_DIR = Path(__file__).parent / "static"

class DirectiveRequest(BaseModel):
    founder_input: str
    auto_approve_risk: bool = True

@app.on_event("startup")
async def startup_event():
    await memory_db.init_db()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    html_file = STATIC_DIR / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding="utf-8")
    return "<h1>LUNA API is live. Static dashboard not found.</h1>"

@app.get("/api/history")
async def get_history():
    history = await memory_db.get_recent_history()
    return JSONResponse(content=history)

@app.get("/api/preferences")
async def get_preferences():
    pref = await memory_db.get_preference("primary_tech_stack")
    return {"primary_tech_stack": pref}

@app.post("/api/directive")
async def execute_directive_rest(req: DirectiveRequest):
    state = LunaGlobalState(founder_input=req.founder_input)
    plan = await engine.plan(req.founder_input, state)
    results = await engine.execute_subtasks(state, founder_approved=req.auto_approve_risk)
    report = await engine.synthesize(state)
    
    # Save to SQLite memory
    await memory_db.save_session(
        founder_input=req.founder_input,
        plan=plan,
        results=results,
        report=report,
        status="completed"
    )

    return {
        "plan": plan.model_dump(),
        "results": {k: v.model_dump() for k, v in results.items()},
        "report": report.model_dump()
    }

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    state: Optional[LunaGlobalState] = None

    try:
        while True:
            data_raw = await websocket.receive_text()
            data = json.loads(data_raw)
            action = data.get("action")

            if action == "directive":
                text = data.get("text", "")
                state = LunaGlobalState(founder_input=text)

                # Step 1: Planning
                plan = await engine.plan(text, state)
                await websocket.send_json({
                    "stage": "planning",
                    "data": plan.model_dump()
                })

                # Step 2: Risk Assessment
                founder_approved = True
                if plan.requires_confirmation:
                    await websocket.send_json({
                        "stage": "risk_check",
                        "data": {
                            "requires_confirmation": True,
                            "confirmation_reason": plan.confirmation_reason
                        }
                    })
                    # Wait for confirmation from websocket
                    confirm_msg_raw = await websocket.receive_text()
                    confirm_msg = json.loads(confirm_msg_raw)
                    founder_approved = confirm_msg.get("approved", False)

                # Step 3: Subtask Parallel Execution
                async def run_and_stream(st):
                    agent = engine.agents.get(st.target_domain, engine.agents["adhoc"])
                    try:
                        res = await agent.execute(st)
                    except Exception as e:
                        from luna.models.schemas import SubTaskResult
                        res = SubTaskResult(
                            task_id=st.task_id,
                            target_domain=st.target_domain,
                            status="failed",
                            output=f"Execution error: {str(e)}"
                        )

                    state.domain_results[st.task_id] = res
                    await websocket.send_json({
                        "stage": "task_complete",
                        "data": {
                            "task_id": st.task_id,
                            "target_domain": st.target_domain,
                            "output": res.output,
                            "status": res.status
                        }
                    })
                    return res

                if not plan.requires_confirmation or founder_approved:
                    tasks = [run_and_stream(st) for st in plan.subtasks]
                    await asyncio.gather(*tasks)
                else:
                    for st in plan.subtasks:
                        from luna.models.schemas import SubTaskResult
                        res = SubTaskResult(
                            task_id=st.task_id,
                            target_domain=st.target_domain,
                            status="skipped",
                            output="Aborted: Action flagged as critical and not confirmed by Founder."
                        )
                        state.domain_results[st.task_id] = res
                        await websocket.send_json({
                            "stage": "task_complete",
                            "data": {
                                "task_id": st.task_id,
                                "target_domain": st.target_domain,
                                "output": res.output,
                                "status": res.status
                            }
                        })

                # Step 4: Executive Synthesis
                report = await engine.synthesize(state)
                await websocket.send_json({
                    "stage": "synthesis",
                    "data": report.model_dump()
                })

                # Step 5: Save to SQLite Memory
                await memory_db.save_session(
                    founder_input=text,
                    plan=plan,
                    results=state.domain_results,
                    report=report,
                    status="completed"
                )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"stage": "error", "message": str(e)})
        except Exception:
            pass
