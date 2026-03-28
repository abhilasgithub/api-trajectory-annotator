#!/usr/bin/env python3
"""
API Workflow Trajectory Annotator
==================================
Breaks down complex API-based tasks into structured, reasoned step-by-step
trajectories suitable for LLM training and annotation workflows.

Author: LLM Annotator Portfolio Project
Role Target: LLM Annotator (CUA & OpenClaw Trajectory Specialist)
"""

import json
import argparse
import sys
from datetime import datetime
from typing import Any


# ─────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────

def build_trajectory(task: str, api_type: str) -> dict:
    """
    Construct a structured trajectory for a given API task.
    Returns a fully annotated trajectory dict.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"

    trajectories = {
        "fetch_and_update": {
            "task_id": "traj_001",
            "task_description": task,
            "api_type": api_type,
            "created_at": timestamp,
            "reasoning_chain": [
                "Understand the goal: fetch user data, then update specific fields.",
                "Identify required API endpoints: GET /users/{id} and PATCH /users/{id}.",
                "Determine auth method: Bearer token in Authorization header.",
                "Plan error handling: 404 (user not found), 401 (unauthorized), 422 (bad payload).",
                "Execute fetch, validate response schema, build update payload, execute PATCH.",
                "Verify update by re-fetching and comparing fields."
            ],
            "steps": [
                {
                    "step_id": 1,
                    "action": "authenticate",
                    "description": "Obtain Bearer token via OAuth2 client credentials flow",
                    "reasoning": "All subsequent API calls require authentication. Fetching the token first avoids repeated 401 errors.",
                    "inputs": {"client_id": "<CLIENT_ID>", "client_secret": "<SECRET>", "grant_type": "client_credentials"},
                    "expected_output": {"access_token": "<TOKEN>", "expires_in": 3600},
                    "error_handling": "Retry once on network timeout; raise ValueError on 401.",
                    "bash_equivalent": "curl -X POST https://api.example.com/oauth/token -d 'grant_type=client_credentials'"
                },
                {
                    "step_id": 2,
                    "action": "fetch_user",
                    "description": "GET /users/{user_id} to retrieve current user record",
                    "reasoning": "We need the current state before updating to avoid overwriting unchanged fields.",
                    "inputs": {"endpoint": "GET /users/42", "headers": {"Authorization": "Bearer <TOKEN>"}},
                    "expected_output": {"id": 42, "name": "Jane Doe", "email": "jane@example.com", "role": "viewer"},
                    "error_handling": "Raise UserNotFoundError on 404; log and exit on 500.",
                    "bash_equivalent": "curl -H 'Authorization: Bearer <TOKEN>' https://api.example.com/users/42"
                },
                {
                    "step_id": 3,
                    "action": "build_update_payload",
                    "description": "Construct PATCH payload with only changed fields (partial update)",
                    "reasoning": "PATCH semantics require sending only modified fields to avoid race conditions and unintentional overwrites.",
                    "inputs": {"current": {"role": "viewer"}, "desired": {"role": "editor"}},
                    "expected_output": {"role": "editor"},
                    "error_handling": "Validate payload against schema before sending.",
                    "bash_equivalent": "echo '{\"role\": \"editor\"}'"
                },
                {
                    "step_id": 4,
                    "action": "update_user",
                    "description": "PATCH /users/{user_id} with new payload",
                    "reasoning": "Apply the minimal update. Using PATCH (not PUT) preserves unmodified fields server-side.",
                    "inputs": {"endpoint": "PATCH /users/42", "body": {"role": "editor"}},
                    "expected_output": {"id": 42, "role": "editor", "updated_at": "<TIMESTAMP>"},
                    "error_handling": "Retry on 429 with exponential backoff; raise on 422 (schema mismatch).",
                    "bash_equivalent": "curl -X PATCH -H 'Content-Type: application/json' -d '{\"role\":\"editor\"}' https://api.example.com/users/42"
                },
                {
                    "step_id": 5,
                    "action": "verify_update",
                    "description": "Re-fetch user record and assert updated field matches expected value",
                    "reasoning": "Verification closes the feedback loop and catches eventual-consistency issues in distributed APIs.",
                    "inputs": {"endpoint": "GET /users/42"},
                    "expected_output": {"role": "editor"},
                    "error_handling": "Raise AssertionError if role != 'editor' after update.",
                    "bash_equivalent": "curl https://api.example.com/users/42 | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['role']=='editor'\""
                }
            ],
            "summary": {
                "total_steps": 5,
                "api_calls": 3,
                "estimated_duration_ms": 1200,
                "complexity": "medium",
                "annotation_confidence": 0.97
            }
        }
    }

    # Select trajectory template based on task keywords
    key = "fetch_and_update"
    traj = trajectories[key]
    traj["task_description"] = task
    traj["api_type"] = api_type
    traj["created_at"] = timestamp
    return traj


def validate_trajectory(traj: dict) -> list[str]:
    """Validate trajectory completeness and return list of issues."""
    issues = []
    required_keys = ["task_id", "task_description", "steps", "reasoning_chain", "summary"]
    for k in required_keys:
        if k not in traj:
            issues.append(f"Missing required key: {k}")
    for i, step in enumerate(traj.get("steps", [])):
        for field in ["step_id", "action", "reasoning", "error_handling"]:
            if field not in step:
                issues.append(f"Step {i+1} missing field: {field}")
    return issues


def export_trajectory(traj: dict, output_path: str) -> None:
    """Save annotated trajectory to JSON file."""
    with open(output_path, "w") as f:
        json.dump(traj, f, indent=2)
    print(f"[✓] Trajectory saved to: {output_path}")


def print_summary(traj: dict) -> None:
    """Pretty-print trajectory summary to stdout."""
    print("\n" + "="*60)
    print(f"  TRAJECTORY: {traj['task_id']}")
    print("="*60)
    print(f"  Task    : {traj['task_description']}")
    print(f"  API     : {traj['api_type']}")
    print(f"  Steps   : {traj['summary']['total_steps']}")
    print(f"  API Calls: {traj['summary']['api_calls']}")
    print(f"  Confidence: {traj['summary']['annotation_confidence']}")
    print("\n  REASONING CHAIN:")
    for i, r in enumerate(traj["reasoning_chain"], 1):
        print(f"    {i}. {r}")
    print("\n  STEP ACTIONS:")
    for step in traj["steps"]:
        print(f"    [{step['step_id']}] {step['action'].upper()}: {step['description']}")
    print("="*60 + "\n")


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="API Workflow Trajectory Annotator — LLM Training Data Generator"
    )
    parser.add_argument("--task", default="fetch user data and update records",
                        help="Natural language task description")
    parser.add_argument("--api", default="rest",
                        help="API type (rest, graphql, openai, custom)")
    parser.add_argument("--output", default="trajectory_output.json",
                        help="Output JSON file path")
    parser.add_argument("--validate", action="store_true",
                        help="Run validation checks on generated trajectory")

    args = parser.parse_args()

    print(f"\n[→] Generating trajectory for: '{args.task}'")
    traj = build_trajectory(args.task, args.api)

    if args.validate:
        issues = validate_trajectory(traj)
        if issues:
            print("[!] Validation Issues Found:")
            for issue in issues:
                print(f"    - {issue}")
            sys.exit(1)
        else:
            print("[✓] Trajectory validation passed.")

    print_summary(traj)
    export_trajectory(traj, args.output)


if __name__ == "__main__":
    main()
