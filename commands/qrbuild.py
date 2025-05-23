Traceback (most recent call last):

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed

    @app_commands.command(name="qrbuild", description="Convert text into a DayZ object QR layout")

     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

           ^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/discord/app_commands/commands.py", line 687, in __init__

                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TypeError: invalid default parameter type given (<class 'discord.app_commands.models.Choice'>), expected (<class 'str'>, <class 'NoneType'>)

 

The above exception was the direct cause of the following exception:

 

    asyncio.run(load_extensions())

  File "/usr/local/lib/python3.12/asyncio/runners.py", line 195, in run

           ^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/asyncio/runners.py", line 118, in run

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/asyncio/base_events.py", line 691, in run_until_complete

  File "/app/bot.py", line 31, in load_extensions

    await bot.load_extension("commands.qrbuild")

  File "/usr/local/lib/python3.12/site-packages/discord/ext/commands/bot.py", line 1029, in load_extension

    await self._load_from_module_spec(spec, name)

    raise errors.ExtensionFailed(key, e) from e

discord.ext.commands.errors.ExtensionFailed: Extension 'commands.qrbuild' raised an error: TypeError: invalid default parameter type given (<class 'discord.app_commands.models.Choice'>), expected (<class 'str'>, <class 'NoneType'>)

Traceback (most recent call last):

  File "/usr/local/lib/python3.12/site-packages/discord/ext/commands/bot.py", line 951, in _load_from_module_spec

    spec.loader.exec_module(lib)  # type: ignore

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "<frozen importlib._bootstrap_external>", line 999, in exec_module

  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed

  File "/app/commands/qrbuild.py", line 10, in <module>

    class QRBuild(commands.Cog):

  File "/app/commands/qrbuild.py", line 20, in QRBuild

    @app_commands.command(name="qrbuild", description="Convert text into a DayZ object QR layout")

     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/discord/app_commands/commands.py", line 2060, in decorator

    return Command(

           ^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/discord/app_commands/commands.py", line 687, in __init__

    self._params: Dict[str, CommandParameter] = _extract_parameters_from_callback(callback, callback.__globals__)

                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/discord/app_commands/commands.py", line 383, in _extract_parameters_from_callback

    param = annotation_to_parameter(resolved, parameter)

            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/discord/app_commands/transformers.py", line 847, in annotation_to_parameter

    raise TypeError(f'invalid default parameter type given ({default.__class__}), expected {valid_types}')

TypeError: invalid default parameter type given (<class 'discord.app_commands.models.Choice'>), expected (<class 'str'>, <class 'NoneType'>)

 

The above exception was the direct cause of the following exception:

 

Traceback (most recent call last):

  File "/app/bot.py", line 40, in <module>

    asyncio.run(load_extensions())

  File "/usr/local/lib/python3.12/asyncio/runners.py", line 195, in run

    return runner.run(main)

           ^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/asyncio/runners.py", line 118, in run

    return self._loop.run_until_complete(task)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/asyncio/base_events.py", line 691, in run_until_complete
