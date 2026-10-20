#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p test-results
cc -std=c11 -Wall -Wextra -Werror tests/time_math_test.c -o test-results/time-math
test-results/time-math
