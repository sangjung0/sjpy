# Reference from https://github.com/facebookresearch/SimulEval.git

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

# MODIFIED FROM ORIGINAL

from typing import Sequence


__all__ = ["AL_score", "LAAL_score", "DAL_score", "AP_score", "average_latency"]


def AL_score(
    delays: Sequence[float], source_length: int, target_length: int | None = None
) -> float:
    # 실제 계산 시간, Source 길이, Target 길이
    # ex: delays = [0, 2, 4, 6, 8], source_length = 4, target_length = 8
    # ASR에서는 delays가 target 길이만큼 존재함, 즉 target은 단어 수, source는 음성의 길이 이다.

    target_length = len(delays) if target_length is None else target_length

    if delays[0] > source_length:
        return delays[0]

    AL = 0
    gamma = target_length / source_length  # 프레임당 이상적인 단어 생성 비율
    tau = 0
    for t_minus_1, d in enumerate(delays):
        # 이상적인 단어 생성 시간과 실제 단어 생성 시간의 차이
        AL += d - t_minus_1 / gamma
        tau = t_minus_1 + 1

        if d >= source_length:
            break
    AL /= tau  # 이상적인 단어 생성 시간 대비 평균 지연 시간
    return AL


def LAAL_score(
    delays: Sequence[float], source_length: int, target_length: int | None = None
) -> float:
    target_length = len(delays) if target_length is None else target_length

    if delays[0] > source_length:
        return delays[0]

    LAAL = 0
    gamma = max(len(delays), target_length) / source_length
    tau = 0
    for t_minus_1, d in enumerate(delays):
        LAAL += d - t_minus_1 / gamma
        tau = t_minus_1 + 1

        if d >= source_length:
            break
    LAAL /= tau
    return LAAL


def DAL_score(delays: Sequence[float], source_length: int) -> float:
    DAL = 0
    target_length = len(delays)
    gamma = target_length / source_length
    g_prime_last = 0
    for i_minus_1, g in enumerate(delays):
        if i_minus_1 + 1 == 1:
            g_prime = g
        else:
            # 이상적인 생성시간 보다 짧으면 이전 생성시간 + 1/gamma 로 보정
            # 따라서, 높은 지연만을 반영하게 됨
            g_prime = max([g, g_prime_last + 1 / gamma])

        DAL += g_prime - i_minus_1 / gamma
        g_prime_last = g_prime

    DAL /= target_length
    return DAL


def AP_score(
    delays: Sequence[float], source_length: int, target_length: int | None = None
) -> float:
    # source 길이와 target 길이의 곱으로 나누어 delays의 합을 나눔
    # 전체 지연 시간을 전체 source 길이에 곱함으로써, 모든 target이 source_length 시점에 생성되었을 때 1이 됨
    # 만약, 0.5라면, 전체 target이 평균적으로 source 길이의 절반 시점에 생성되었음을 의미
    # 따라서, 값이 작을수록 지연이 적음을 의미
    # 즉, 전체 소스 길이 대비, 이 토큰이 나온 시점이 얼마나 늦었는지의 평균 비율
    target_length = len(delays) if target_length is None else target_length
    return sum(delays) / (source_length * target_length)


def average_latency(delays: Sequence[float]) -> float:
    return sum(delays) / len(delays)
