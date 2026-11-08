![Tide staff close up on the harbour wall, its plain black and white bands rising above the returning water, the orange marker float riding large at its base and fishing boats afloat behind](intro-banner.png)

# analyze-process-behavior

![Harbour wall at low water with the banded tide staff at its centre right, the sea fallen to the lowest bands, wet stone and weed below the waterline, fishing boats resting on the harbour floor behind and one orange marker float tied at the staff's base](banner.png)

![Vertical tide staff straight on fixed to a grey harbour wall, plain black and white bands with no numerals or letters anywhere, the green water standing at its base and one small orange marker float bobbing beside it](logo.png)

![Night field scene: the light pyramid thins from its base across a long cycle, the vane turns once and holds, and the grass heads bend once at the brightest point](scene.svg)


# analyze-process-behavior
Samples a named process on Linux through /proc at the start and end of a sampling window and reports measured values and deltas: process state, thread count, user and system CPU ticks, voluntary and nonvoluntary context switches, read and write syscall counters and byte counters where readable, open file descriptor count, and child PIDs. The CSV carries the PID and the sampling duration, and each row is a measured quantity. The report includes a context switches per second rate as a number only; it makes no anomaly or malicious activity verdict. A PID that does not exist, or that exits during sampling, ends the run at exit 1. - Focused on Data analysis and reporting

> Dark sky note: a PID that does not exist, or that exits during sampling, ends the run at exit 1. That is the condition a first time user is most likely to trip over, stated where the measured list is given.


![Minor section divider: a copper rule with a single blink at its centre](sep-light.svg)

## Install
`git clone https://github.com/ShadowGuardAI/analyze-process-behavior`

> Dark sky note: the clone address above names the account as ShadowGuardAI without a hyphen, while the repository itself sits under ShadowGuard-AI. The line is preserved as written, so correct it by hand if you copy it.


![Major section divider: a satellite crossing the full width on a copper rule, blinking at long intervals](sep-heavy.svg)

## Usage
`./analyze-process-behavior [params]`


![Minor section divider: a copper rule with a single blink at its centre](sep-light.svg)

## Parameters
- `-h`: Show help message and exit
- `-p`: Process ID to analyze.  If not provided, attempts to trace the current process.
- `-o`: Output CSV file to store the analysis results (default: process_analysis.csv).
- `-t`: Duration in seconds to sample the process (default: 10 seconds).
- `-l`: Set the logging level (default: INFO).


![Major section divider: a satellite crossing the full width on a copper rule, blinking at long intervals](sep-heavy.svg)

## License
Copyright (c) ShadowGuardAI
