---
name: assign-maus
description: >
  Use when deploying or assigning work through OpenMausBot MCP: creating
  role-based bots, grouping them into a channel, sending kickoff messages, and
  assigning tasks to a bot. Triggers on "deploy AI", "assign task to bot",
  "OpenMausBot", "create channel", or "kickoff team".
---

# Assign Maus

Use OpenMausBot MCP to deploy AI bots and assign work to them. This skill
covers the full flow from health check to task assignment.

## Prerequisites

- OpenMausBot server reachable (default `http://127.0.0.1:8799`)
- At least one available model instance (check with `list_available_models`)
- If Paperclip must be running for this workflow, run `paperclip-launch` first.

## 1. Health check

```js
tools.openmausbot.get_system_health()
```

Done when: `status` is `connected`.

## 2. List existing bots

```js
tools.openmausbot.list_bots()
```

Use this to avoid duplicate names and to get existing bot IDs.

## 3. Create role-based bots

```js
tools.openmausbot.create_bot({
  name: "CEO",
  title: "Chief Executive Officer",
  description: "Company strategy, priorities, and coordination.",
  section: "EcoNova",
  instance_id: "opencodeGo",
  model: "opencode/beam-free"
})
```

Repeat for each role. Store the returned `bot.id` and `activeTaskId`.

Done when: each bot returns `success: true` with a valid `id`.

## 4. Create a team channel

```js
tools.openmausbot.create_channel({
  name: "EcoNova-Team",
  member_ids: ["<botId1>", "<botId2>", "..."],
  section: "EcoNova",
  bulletin: "Role descriptions and coordination rules.",
  default_responder: { kind: "mentions" }
})
```

Use `mentions` as the default responder so only @mentioned bots reply.

Done when: channel returns `success: true` with an `id`.

## 5. Send a kickoff message

```js
tools.openmausbot.send_channel_message({
  channel_id: "<channelId>",
  text: "Kickoff: ..."
})
```

Done when: message returns `success: true` with a `messageId`.

## 6. Assign a task to a bot

Create a task first, then send the instruction:

```js
const task = await tools.openmausbot.create_task({
  target_type: "bot",
  target_id: "<botId>",
  title: "Task title"
})

await tools.openmausbot.send_bot_message({
  bot_id: "<botId>",
  task_id: task.task.taskId,
  text: "Detailed instruction in Traditional Chinese."
})
```

Done when: both calls return `success: true`.

## 7. Wait for completion (optional)

```js
tools.openmausbot.wait_for_conversation({
  target_type: "bot",
  target_id: "<botId>",
  task_id: "<taskId>",
  timeout_seconds: 120
})
```

## Notes

- Model instance IDs and available models come from `list_available_models`.
- For plan stress-testing before assignment, optionally hook `grill-me`.
- `create_task` returns a new task; use its `taskId` in `send_bot_message`.
- `default_responder: { kind: "mentions" }` prevents all bots from replying at once.
- Keep task instructions in Traditional Chinese (繁體中文) per company language policy.
- Bot profiles can be updated later with `update_bot_profile`.

## Common mistakes

- Forgetting to pass `task_id` to `send_bot_message` (it defaults to the selected task, which may not be the new one).
- Using `default_responder: { kind: "everyone" }` in a large team (causes noisy replies).
- Creating duplicate bots without checking `list_bots` first.
EOF
echo "written"; sed -n '1,12p' /home/sam/.agents/skills/assign-maus/SKILL.md