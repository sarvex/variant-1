# MPark.Variant
#
# Copyright Michael Park, 2015-2017
#
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE.md or copy at http://boost.org/LICENSE_1_0.txt)

import os
import pprint
import subprocess

result = {}

std_flags = os.getenv('STDFLAGS')
for std_flag in std_flags.split() if std_flags is not None else ['']:
  os.environ['CXXFLAGS'] = std_flag
  for exceptions in ['OFF', 'ON']:
    config = f'{filter(str.isalnum, std_flag)}-{exceptions}'
    build_dir = f'build-{config}'
    os.mkdir(build_dir)
    os.chdir(build_dir)
    result[config] = {
        'Configure': None,
        'Build-Debug': None,
        'Build-Release': None,
        'Test-Debug': None,
        'Test-Release': None
    }

    tests = os.environ['TESTS'].split()
    if std_flag.endswith(('11', '1y', '14', '1z')) and 'libc++' in tests:
      tests.remove('libc++')

    configure = [
        'cmake',
        '-G',
        os.environ['GENERATOR'],
        f'-DMPARK_VARIANT_EXCEPTIONS={exceptions}',
        f"-DMPARK_VARIANT_INCLUDE_TESTS={';'.join(tests)}",
        '..',
    ]
    result[config]['Configure'] = subprocess.call(configure)
    if result[config]['Configure'] == 0:
      for build_type in ['Debug', 'Release']:
        result[config][f'Build-{build_type}'] = subprocess.call(
            ['cmake', '--build', '.', '--config', build_type])
        if result[config][f'Build-{build_type}'] == 0:
          result[config][f'Test-{build_type}'] = subprocess.call(
              ['ctest', '--output-on-failure', '--build-config', build_type])
    os.chdir('..')

pprint.pprint(result)
exit(any(status != 0 for d in result.itervalues() for status in d.itervalues()))
