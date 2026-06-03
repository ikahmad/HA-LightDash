# Release Notes for v0.10.14 (2026-06-03)

This release fixes a memory issue that could cause the addon to crash unexpectedly, and adds better diagnostics to monitor memory usage over time.

- **Fixed a crash caused by memory build-up.** Some SSE (Server-Sent Events) client queues could grow without limit if a client disconnected slowly, eventually running out of memory and causing the container to be killed. Each queue is now capped at 256 messages, and slow clients are cleaned up automatically.
- **Better diagnostics for memory monitoring.** LightDash now logs a heartbeat every 5 minutes showing memory usage (RSS), uptime, and how many SSE clients are connected. This will help spot memory trends before they become a problem.
