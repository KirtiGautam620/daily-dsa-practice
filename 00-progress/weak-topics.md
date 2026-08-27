## 🧠 Learning Gap — `zip()` + unpacking

While solving **Longest Common Prefix**, I realized I didn't have a clear mental model of how `zip(*strs)` works.

### What I was missing

- `zip()` combines corresponding elements from multiple iterables.
- A string is an iterable of characters.
- `*` unpacks a list into separate arguments.

So:

```python
strs = ["flower", "flow", "flight"]

zip(*strs)