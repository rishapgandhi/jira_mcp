"""Jira tools — search, get, create, update, transition, comment, assign."""

from mcp.types import Tool
from src.client import get_client, get_project_key

JIRA_TOOLS = [
    Tool(name="jira_search", description="Search issues using JQL (Jira Query Language)", inputSchema={"type": "object", "properties": {"jql": {"type": "string", "description": "JQL query (e.g. 'status=Open AND assignee=currentUser()')"}, "max_results": {"type": "integer", "default": 20}}, "required": ["jql"]}),
    Tool(name="jira_get_issue", description="Get full details of a Jira issue by key (e.g. PV-123)", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}}, "required": ["issue_key"]}),
    Tool(name="jira_create_issue", description="Create a new Jira issue", inputSchema={"type": "object", "properties": {"summary": {"type": "string"}, "description": {"type": "string", "default": ""}, "issue_type": {"type": "string", "default": "Task"}, "priority": {"type": "string", "default": "Medium"}, "assignee_email": {"type": "string", "default": ""}, "labels": {"type": "string", "description": "Comma-separated labels", "default": ""}}, "required": ["summary"]}),
    Tool(name="jira_update_issue", description="Update fields on an existing issue", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}, "summary": {"type": "string", "default": ""}, "description": {"type": "string", "default": ""}, "priority": {"type": "string", "default": ""}, "labels": {"type": "string", "default": ""}}, "required": ["issue_key"]}),
    Tool(name="jira_transition", description="Transition an issue to a new status (e.g. In Progress, Done)", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}, "status": {"type": "string", "description": "Target status name (e.g. 'In Progress', 'Done')"}}, "required": ["issue_key", "status"]}),
    Tool(name="jira_add_comment", description="Add a comment to a Jira issue (supports rich text)", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}, "comment": {"type": "string"}}, "required": ["issue_key", "comment"]}),
    Tool(name="jira_delete_comment", description="Delete a comment from a Jira issue", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}, "comment_id": {"type": "string"}}, "required": ["issue_key", "comment_id"]}),
    Tool(name="jira_list_comments", description="List all comments on a Jira issue", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}}, "required": ["issue_key"]}),
    Tool(name="jira_assign", description="Assign an issue to a user", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}, "assignee_id": {"type": "string", "description": "Atlassian account ID of the assignee"}}, "required": ["issue_key", "assignee_id"]}),
    Tool(name="jira_my_issues", description="Get issues assigned to me or created by me", inputSchema={"type": "object", "properties": {"filter": {"type": "string", "enum": ["assigned", "created", "watching"], "default": "assigned"}}, "required": []}),
    Tool(name="jira_sprint_issues", description="Get issues in the active sprint", inputSchema={"type": "object", "properties": {"status": {"type": "string", "description": "Filter by status (optional)", "default": ""}}, "required": []}),
    Tool(name="jira_attach_file", description="Attach a file to a Jira issue", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}, "file_path": {"type": "string", "description": "Absolute path to the file to attach"}}, "required": ["issue_key", "file_path"]}),
    Tool(name="jira_delete_attachment", description="Delete an attachment from a Jira issue", inputSchema={"type": "object", "properties": {"attachment_id": {"type": "string"}}, "required": ["attachment_id"]}),
    Tool(name="jira_list_attachments", description="List all attachments on a Jira issue", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}}, "required": ["issue_key"]}),
    Tool(name="jira_get_transitions", description="Get available status transitions for an issue", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}}, "required": ["issue_key"]}),
    Tool(name="jira_link_issues", description="Create a link between two issues", inputSchema={"type": "object", "properties": {"inward_issue": {"type": "string", "description": "Issue key (e.g. PV-100)"}, "outward_issue": {"type": "string", "description": "Issue key (e.g. PV-200)"}, "link_type": {"type": "string", "description": "e.g. 'Blocks', 'is blocked by', 'Relates', 'Duplicate'", "default": "Relates"}}, "required": ["inward_issue", "outward_issue"]}),
    Tool(name="jira_get_project_info", description="Get project details, issue types, and statuses", inputSchema={"type": "object", "properties": {"project_key": {"type": "string", "default": ""}}, "required": []}),
    Tool(name="jira_list_users", description="Search for users in the Jira instance", inputSchema={"type": "object", "properties": {"query": {"type": "string", "description": "Name or email to search"}}, "required": ["query"]}),
    Tool(name="jira_log_work", description="Log work/time on an issue", inputSchema={"type": "object", "properties": {"issue_key": {"type": "string"}, "time_spent": {"type": "string", "description": "e.g. '2h', '1d', '30m'"}, "comment": {"type": "string", "default": ""}}, "required": ["issue_key", "time_spent"]}),
]


async def handle_jira(name: str, args: dict) -> str:
    c = get_client()
    project = get_project_key()

    if name == "jira_search":
        jql = args["jql"]
        if project and "project" not in jql.lower():
            jql = f"project={project} AND {jql}"
        r = c.get("/search/jql", params={"jql": jql, "maxResults": args.get("max_results", 20), "fields": "summary,status,assignee,priority,issuetype,created,updated"})
        r.raise_for_status()
        issues = r.json().get("issues", [])
        if not issues:
            return "No issues found."
        lines = []
        for i in issues:
            f = i["fields"]
            assignee = f.get("assignee", {})
            lines.append(f"{i['key']} | {f.get('issuetype',{}).get('name','')} | {f['summary']} | {f.get('status',{}).get('name','')} | {f.get('priority',{}).get('name','')} | {assignee.get('displayName','Unassigned') if assignee else 'Unassigned'}")
        return "\n".join(lines)

    elif name == "jira_get_issue":
        r = c.get(f"/issue/{args['issue_key']}")
        r.raise_for_status()
        i = r.json()
        f = i["fields"]
        assignee = f.get("assignee", {})
        comments = f.get("comment", {}).get("comments", [])[-5:]
        comment_text = "\n".join(f"  - {cm.get('author',{}).get('displayName','')}: {cm.get('body','')[:200]}" for cm in comments)
        return (
            f"Key: {i['key']}\n"
            f"Type: {f.get('issuetype',{}).get('name','')}\n"
            f"Summary: {f['summary']}\n"
            f"Status: {f.get('status',{}).get('name','')}\n"
            f"Priority: {f.get('priority',{}).get('name','')}\n"
            f"Assignee: {assignee.get('displayName','Unassigned') if assignee else 'Unassigned'}\n"
            f"Reporter: {f.get('reporter',{}).get('displayName','')}\n"
            f"Created: {f.get('created','')[:10]}\n"
            f"Updated: {f.get('updated','')[:10]}\n"
            f"Description: {(f.get('description') or '')[:500]}\n"
            f"Labels: {', '.join(f.get('labels', []))}\n"
            f"Recent Comments:\n{comment_text or '  (none)'}"
        )

    elif name == "jira_create_issue":
        proj = project or args.get("project_key", "")
        if not proj:
            return "Error: Set JIRA_PROJECT_KEY in env or provide project_key"
        fields = {
            "project": {"key": proj},
            "summary": args["summary"],
            "issuetype": {"name": args.get("issue_type", "Task")},
            "priority": {"name": args.get("priority", "Medium")},
        }
        if args.get("description"):
            fields["description"] = args["description"]
        if args.get("labels"):
            fields["labels"] = [l.strip() for l in args["labels"].split(",")]
        if args.get("assignee_email"):
            # Search for user by email
            ur = c.get("/user/search", params={"query": args["assignee_email"]})
            if ur.status_code == 200 and ur.json():
                fields["assignee"] = {"accountId": ur.json()[0]["accountId"]}
        r = c.post("/issue", json={"fields": fields})
        r.raise_for_status()
        key = r.json()["key"]
        base = c.base_url.host
        return f"Issue created: {key}\nURL: https://{base}/browse/{key}"

    elif name == "jira_update_issue":
        fields = {}
        if args.get("summary"):
            fields["summary"] = args["summary"]
        if args.get("description"):
            fields["description"] = args["description"]
        if args.get("priority"):
            fields["priority"] = {"name": args["priority"]}
        if args.get("labels"):
            fields["labels"] = [l.strip() for l in args["labels"].split(",")]
        if not fields:
            return "No fields to update."
        r = c.put(f"/issue/{args['issue_key']}", json={"fields": fields})
        r.raise_for_status()
        return f"Updated {args['issue_key']}"

    elif name == "jira_transition":
        # Get available transitions
        r = c.get(f"/issue/{args['issue_key']}/transitions")
        r.raise_for_status()
        transitions = r.json().get("transitions", [])
        target = args["status"].lower()
        match = next((t for t in transitions if t["name"].lower() == target), None)
        if not match:
            available = ", ".join(t["name"] for t in transitions)
            return f"Cannot transition to '{args['status']}'. Available: {available}"
        r = c.post(f"/issue/{args['issue_key']}/transitions", json={"transition": {"id": match["id"]}})
        r.raise_for_status()
        return f"Transitioned {args['issue_key']} → {args['status']}"

    elif name == "jira_add_comment":
        comment_body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": args["comment"]}]}]
            }
        }
        import httpx as _httpx
        import os as _os
        from base64 import b64encode as _b64
        base_url = _os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        email = _os.environ.get("JIRA_EMAIL", "")
        token = _os.environ.get("JIRA_API_TOKEN", "")
        auth = _b64(f"{email}:{token}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        r = _httpx.post(f"{base_url}/rest/api/3/issue/{args['issue_key']}/comment", headers=headers, json=comment_body, timeout=30)
        r.raise_for_status()
        return f"Comment added to {args['issue_key']}"

    elif name == "jira_delete_comment":
        import httpx as _httpx
        import os as _os
        from base64 import b64encode as _b64
        base_url = _os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        email = _os.environ.get("JIRA_EMAIL", "")
        token = _os.environ.get("JIRA_API_TOKEN", "")
        auth = _b64(f"{email}:{token}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        r = _httpx.delete(f"{base_url}/rest/api/3/issue/{args['issue_key']}/comment/{args['comment_id']}", headers=headers, timeout=30)
        r.raise_for_status()
        return f"Comment {args['comment_id']} deleted from {args['issue_key']}"

    elif name == "jira_list_comments":
        import httpx as _httpx
        import os as _os
        from base64 import b64encode as _b64
        base_url = _os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        email = _os.environ.get("JIRA_EMAIL", "")
        token = _os.environ.get("JIRA_API_TOKEN", "")
        auth = _b64(f"{email}:{token}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        r = _httpx.get(f"{base_url}/rest/api/3/issue/{args['issue_key']}/comment", headers=headers, timeout=30)
        r.raise_for_status()
        comments = r.json().get("comments", [])
        if not comments:
            return "No comments."
        lines = []
        for cm in comments:
            body_text = ""
            for block in cm.get("body", {}).get("content", []):
                for item in block.get("content", []):
                    body_text += item.get("text", "")
            lines.append(f"ID: {cm['id']} | {cm.get('author',{}).get('displayName','')} | {cm.get('created','')[:16]} | {body_text[:100]}")
        return "\n".join(lines)

    elif name == "jira_assign":
        r = c.put(f"/issue/{args['issue_key']}/assignee", json={"accountId": args["assignee_id"]})
        r.raise_for_status()
        return f"Assigned {args['issue_key']} to {args['assignee_id']}"

    elif name == "jira_my_issues":
        filter_type = args.get("filter", "assigned")
        jql_map = {
            "assigned": "assignee=currentUser() ORDER BY updated DESC",
            "created": "reporter=currentUser() ORDER BY created DESC",
            "watching": "watcher=currentUser() ORDER BY updated DESC",
        }
        jql = jql_map.get(filter_type, jql_map["assigned"])
        if project:
            jql = f"project={project} AND {jql}"
        r = c.get("/search/jql", params={"jql": jql, "maxResults": 20, "fields": "summary,status,priority,issuetype"})
        r.raise_for_status()
        issues = r.json().get("issues", [])
        if not issues:
            return "No issues found."
        return "\n".join(f"{i['key']} | {i['fields'].get('status',{}).get('name','')} | {i['fields']['summary']}" for i in issues)

    elif name == "jira_sprint_issues":
        jql = "sprint in openSprints()"
        if project:
            jql = f"project={project} AND {jql}"
        if args.get("status"):
            jql += f" AND status='{args['status']}'"
        jql += " ORDER BY rank ASC"
        r = c.get("/search/jql", params={"jql": jql, "maxResults": 50, "fields": "summary,status,assignee,priority,issuetype"})
        r.raise_for_status()
        issues = r.json().get("issues", [])
        if not issues:
            return "No sprint issues found."
        lines = []
        for i in issues:
            f = i["fields"]
            assignee = f.get("assignee", {})
            lines.append(f"{i['key']} | {f.get('status',{}).get('name','')} | {f['summary']} | {assignee.get('displayName','Unassigned') if assignee else 'Unassigned'}")
        return "\n".join(lines)

    elif name == "jira_attach_file":
        import os as _os
        file_path = args["file_path"]
        if not _os.path.isfile(file_path):
            return f"Error: File not found: {file_path}"
        filename = _os.path.basename(file_path)
        base_url = _os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        from base64 import b64encode as _b64
        email = _os.environ.get("JIRA_EMAIL", "")
        token = _os.environ.get("JIRA_API_TOKEN", "")
        auth = _b64(f"{email}:{token}".encode()).decode()
        import httpx as _httpx
        with open(file_path, "rb") as f:
            r = _httpx.post(
                f"{base_url}/rest/api/3/issue/{args['issue_key']}/attachments",
                headers={"Authorization": f"Basic {auth}", "X-Atlassian-Token": "no-check"},
                files={"file": (filename, f)},
                timeout=30,
            )
        if r.status_code in [200, 201]:
            return f"✅ File '{filename}' attached to {args['issue_key']}"
        return f"Error: {r.status_code} {r.text[:200]}"

    elif name == "jira_delete_attachment":
        import httpx as _httpx
        import os as _os
        from base64 import b64encode as _b64
        base_url = _os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        email = _os.environ.get("JIRA_EMAIL", "")
        token = _os.environ.get("JIRA_API_TOKEN", "")
        auth = _b64(f"{email}:{token}".encode()).decode()
        r = _httpx.delete(f"{base_url}/rest/api/3/attachment/{args['attachment_id']}", headers={"Authorization": f"Basic {auth}"}, timeout=30)
        if r.status_code == 204:
            return f"✅ Attachment {args['attachment_id']} deleted"
        return f"Error: {r.status_code} {r.text[:200]}"

    elif name == "jira_list_attachments":
        import httpx as _httpx
        import os as _os
        from base64 import b64encode as _b64
        base_url = _os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        email = _os.environ.get("JIRA_EMAIL", "")
        token = _os.environ.get("JIRA_API_TOKEN", "")
        auth = _b64(f"{email}:{token}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        r = _httpx.get(f"{base_url}/rest/api/3/issue/{args['issue_key']}?fields=attachment", headers=headers, timeout=30)
        r.raise_for_status()
        attachments = r.json().get("fields", {}).get("attachment", [])
        if not attachments:
            return "No attachments."
        return "\n".join(f"ID: {a['id']} | {a['filename']} | {a.get('size',0)//1024}KB | {a.get('created','')[:16]}" for a in attachments)

    elif name == "jira_get_transitions":
        r = c.get(f"/issue/{args['issue_key']}/transitions")
        r.raise_for_status()
        transitions = r.json().get("transitions", [])
        if not transitions:
            return "No transitions available."
        return "\n".join(f"ID: {t['id']} | {t['name']}" for t in transitions)

    elif name == "jira_link_issues":
        r = c.post("/issueLink", json={
            "type": {"name": args.get("link_type", "Relates")},
            "inwardIssue": {"key": args["inward_issue"]},
            "outwardIssue": {"key": args["outward_issue"]},
        })
        r.raise_for_status()
        return f"✅ Linked {args['inward_issue']} → {args['outward_issue']} ({args.get('link_type', 'Relates')})"

    elif name == "jira_get_project_info":
        proj = args.get("project_key") or project
        if not proj:
            return "Error: No project key provided or configured"
        r = c.get(f"/project/{proj}")
        r.raise_for_status()
        p = r.json()
        issue_types = ", ".join(it["name"] for it in p.get("issueTypes", []))
        return f"Project: {p['name']} ({p['key']})\nLead: {p.get('lead',{}).get('displayName','')}\nIssue Types: {issue_types}\nURL: {p.get('self','')}"

    elif name == "jira_list_users":
        r = c.get("/user/search", params={"query": args["query"], "maxResults": 10})
        r.raise_for_status()
        users = r.json()
        if not users:
            return "No users found."
        return "\n".join(f"ID: {u['accountId']} | {u.get('displayName','')} | {u.get('emailAddress','')}" for u in users)

    elif name == "jira_log_work":
        body = {"timeSpent": args["time_spent"]}
        if args.get("comment"):
            body["comment"] = {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": args["comment"]}]}]
            }
        r = c.post(f"/issue/{args['issue_key']}/worklog", json=body)
        r.raise_for_status()
        return f"✅ Logged {args['time_spent']} on {args['issue_key']}"

    return "Unknown jira tool"
