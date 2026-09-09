"""Just the baseline, many times: how often does a cap-out position actually run away?

The recorded build ran the window dry at these positions, but resampling one of them 4 times cost
1,468 tokens a turn and never failed. If the failure is a tail, its RATE is the only thing an arm
can be measured against — and an arm compared on a failure that is not happening measures noise.
"""
import probe

ARMS = [probe.Arm("baseline", lambda w, m: [dict(x) for x in m])]
