#!/usr/bin/env python3
"""去掉 setlocalversion 生成的 -dirty 后缀。

打了补丁之后源码树是脏的，setlocalversion 会在版本串末尾追加 -dirty，
导致 kernel.release 变成 5.10.236-android12-9-o-g<sha>-dirty。模块 vermagic
里带的就是这个串，一旦与官方 vendor_dlkm 里的模块不一致，所有厂商模块都会
拒绝加载（表现为没 WiFi、没相机、没指纹，以及系统服务反复重试导致卡顿）。

这个脚本在 res="$(scm_version)" 之后追加 res="${res%-dirty}"，只砍掉 -dirty，
保留 -g<sha>，使内核与官方模块的 vermagic 完全一致。
"""
import pathlib
import sys

MARK = "${res%-dirty}"
ANCHOR = '\tres="$res$(scm_version)"\n'


def patch(path: pathlib.Path) -> None:
    if not path.is_file():
        print(f"[skip] not found: {path}")
        return
    text = path.read_text()
    if MARK in text:
        print(f"[skip] already patched: {path}")
        return
    if ANCHOR not in text:
        print(f"[warn] anchor not found, left untouched: {path}")
        return
    inject = (
        ANCHOR
        + "\t# MT-ROOT: 去掉 -dirty，保证与官方 vendor_dlkm 模块 vermagic 一致\n"
        + '\tres="${res%-dirty}"\n'
    )
    path.write_text(text.replace(ANCHOR, inject, 1))
    print(f"[ok] patched: {path}")


def main() -> int:
    for arg in sys.argv[1:]:
        patch(pathlib.Path(arg))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
