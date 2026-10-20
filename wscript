import os

top = '.'
out = 'build'


def options(ctx):
    ctx.load('pebble_sdk')


def configure(ctx):
    ctx.load('pebble_sdk')


def build(ctx):
    ctx.load('pebble_sdk')
    binaries = []
    cached_env = ctx.env
    for platform in ctx.env.TARGET_PLATFORMS:
        ctx.env = ctx.all_envs[platform]
        ctx.set_group(ctx.env.PLATFORM_NAME)
        # Optional battery build; default retains the requested seconds hand.
        if os.environ.get('PEBBLIER_SECONDS', '1') == '0':
            ctx.env.append_value('DEFINES', ['PEBBLIER_SECONDS=0'])
        # Deterministic QEMU visual tests, never used by the release workflow.
        fixture = os.environ.get('PEBBLIER_FIXTURE')
        if fixture:
            values = [int(part) for part in fixture.split(':')]
            if len(values) != 4 or not (0 <= values[0] < 24 and 0 <= values[1] < 60
                                      and 0 <= values[2] < 60 and 1 <= values[3] <= 31):
                ctx.fatal('PEBBLIER_FIXTURE must be hour:minute:second:day')
            ctx.env.append_value('DEFINES', ['PEBBLIER_TEST_{}={}'.format(key, value)
                for key, value in zip(['HOUR', 'MINUTE', 'SECOND', 'DAY'], values)])
        elf = '{}/pebble-app.elf'.format(ctx.env.BUILD_DIR)
        ctx.pbl_build(source=ctx.path.ant_glob('src/c/**/*.c'), target=elf, bin_type='app')
        binaries.append({'platform': platform, 'app_elf': elf})
    ctx.env = cached_env
    ctx.set_group('bundle')
    ctx.pbl_bundle(binaries=binaries)
