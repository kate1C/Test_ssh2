from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Mini Tasks API", version="1.0.0")


class TaskIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    done: bool = False


class Task(TaskIn):
    id: int


DB: dict[int, Task] = {}
_next_id = 1


@app.get("/tasks", response_model=list[Task], tags=["tasks"])
def list_tasks():
    return list(DB.values())


@app.get("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def get_task(task_id: int):
    if task_id not in DB:
        raise HTTPException(404, "Task not found")
    return DB[task_id]


@app.post("/tasks", response_model=Task,
          status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskIn):
    global _next_id
    task = Task(id=_next_id, **payload.model_dump())
    DB[_next_id] = task
    _next_id += 1
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT,
            tags=["tasks"])
def delete_task(task_id: int):
    if DB.pop(task_id, None) is None:
        raise HTTPException(404, "Task not found")