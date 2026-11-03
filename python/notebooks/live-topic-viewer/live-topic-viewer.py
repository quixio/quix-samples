"""Live topic viewer: show the latest messages of the first Kafka topic.

Needs a topic with data in this workspace.
"""

import quixlab as ql

canvas = ql.Canvas(title="Live topic viewer")


@canvas.cell(position=(60, 0), size=(900, 140), code_height=240)
def inputs_check():
    import os
    from quixlab.quix_platform import list_topics
    workspace = os.environ.get("Quix__Workspace__Id", "")
    if not workspace:
        return ql.ui.markdown("**No workspace id found.** Open this notebook inside a Quix workspace.")
    try:
        names = [t["name"] for t in list_topics(workspace)]
    except Exception as exc:
        return ql.ui.markdown(f"**The topic list is not reachable.** ({type(exc).__name__})")
    if not names:
        return ql.ui.markdown("**This workspace has no topic yet.** Create a topic that gets data, then run this notebook again.")
    return ql.ui.markdown(f"Ready. The first topic is `{names[0]}`. Change the name in the next cell to use another topic.")


@canvas.stream(position=(60, 160), size=(900, 360), code_height=240)
def messages(inputs_check):
    import os
    from quixlab.quix_platform import list_topics
    workspace = os.environ.get("Quix__Workspace__Id", "")
    names = [t["name"] for t in list_topics(workspace)] if workspace else []
    return ql.topic(names[0] if names else "no-topic", workspace=workspace, offset="latest", limit=200)


if __name__ == "__main__":
    canvas.serve()
