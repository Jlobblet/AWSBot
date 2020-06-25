class HELPTEXTS:
    class START:
        brief = "Start an instance by passing its friendly name."
        full = """Start an instance by passing its friendly name.

Syntax is start <friendly_name>.
If the instance cannot be found, is already running, or on cooldown, do nothing."""

    class STOP:
        brief = "Stop an instance by passing its friendly name."
        full = """Stop an intance by passing its friendly name.

Syntax is stop <friendly_name>.
If the instance cannot be found, or is already stopped, do nothing."""

    class SHOW:
        brief = "Show a list of all instances that can be controlled from this guild."
        full = """Show a list of all instances that can be controlled from this guild.

Syntax is show."""

    class DESCRIBE:
        brief = "Describe the current state of an instance."
        full = """Describe the current state of an instance.

Syntax is describe <friendly_name>.
Shows current status, launch time, uptime, cooldown if applicable.
If the instance cannot be found, do nothing."""

    class ADD:
        brief = "Add a new EC2 instance and friendly name to the database."
        full = """Add a new EC2 instance and friendly name to the database.

Command is restricted so that only I can run it.
Syntax is add <friendly_name> <instance_id>.
If the instance cannot be found, do not add it.
If the friendly_name is already in the table, do nothing and alert the user."""

    class REMOVE:
        brief = "Remove an EC2 instance and friendly name from the databse."
        full = """Remove an EC2 instance and friendly name from the database.

Command is restricted so that only I can run it.
Syntax is remove <friendly_name>.
If the instance cannot be found, do nothing."""
