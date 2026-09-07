#!/usr/bin/env python3
"""PreToolUse guard hook for /implement-feature.

Does three jobs on every Read/Bash/Grep/Glob (for the conductor AND every subagent):
  1. AUDIT  — append one JSONL line per tool call (agent_id/agent_type/tool/target).
  2. SECRETS GUARDRAIL — deny reads of .env / keys / credentials for ANY agent.
  3. ALGORITHM-BLIND — deny reads of design-internal.md for the test-writer agent only.

Reads the hook JSON on stdin. To DENY: print a hookSpecificOutput deny decision and
exit 2. To ALLOW: exit 0.

Run-log path: $IF_RUNLOG, else $CLAUDE_PROJECT_DIR/if-runlog.jsonl, else
/tmp/if-runlog.jsonl.
"""
import json, os, sys, datetime

def runlog_path():
    return (os.environ.get("IF_RUNLOG")
            or (os.path.join(os.environ["CLAUDE_PROJECT_DIR"], "if-runlog.jsonl")
                if os.environ.get("CLAUDE_PROJECT_DIR") else None)
            or "/tmp/if-runlog.jsonl")

# --- secret patterns (basename / path fragments) ---
SECRET_HINTS = (".env", "id_rsa", "id_ed25519", "credentials", ".pem", ".key",
                ".ssh/", ".aws/credentials", "secrets.", ".netrc", ".pgpass")

def looks_secret(target: str) -> bool:
    t = target.lower()
    base = os.path.basename(t)
    if base == ".env" or base.startswith(".env") or base.endswith((".pem", ".key")):
        return True
    return any(h in t for h in SECRET_HINTS)

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # never break the tool on a parse error

    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}
    agent_type = str(data.get("agent_type") or "")
    agent_id = str(data.get("agent_id") or "")
    target = str(ti.get("file_path") or ti.get("path") or ti.get("command")
                 or ti.get("pattern") or "")

    # 1. AUDIT (best-effort; never fail the tool because of logging)
    try:
        with open(runlog_path(), "a") as f:
            f.write(json.dumps({
                "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                "agent_type": agent_type, "agent_id": agent_id,
                "tool": tool, "target": target[:300],
            }) + "\n")
    except Exception:
        pass

    def deny(reason):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))
        sys.exit(2)

    # 2. SECRETS GUARDRAIL — any agent, any read-ish tool
    if looks_secret(target):
        deny(f"Blocked by implement-feature guard: reading secrets/.env is not allowed "
             f"(target: {os.path.basename(target) or target[:60]}).")

    # 3. ALGORITHM-BLIND — only the test-writer is denied design-internal
    if "test-writer" in agent_type and "design-internal" in target:
        deny("Blocked by implement-feature guard: the test-writer is algorithm-blind and "
             "must not read design-internal.md.")

    sys.exit(0)

if __name__ == "__main__":
    main()
