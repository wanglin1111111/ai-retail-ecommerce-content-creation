#!/usr/bin/env python3
"""ai-retail-ecommerce-content-creation 技能验证脚本。

断言"产出=合规成立"而非"动作已执行"：
- GOOD 样例：含全部合规要素，且无违规 → exit 0
- BAD 样例：命中任一违规模式 → exit 1

退出码契约：0=通过，1=存在错误，2=文件错误。
"""
import re
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_FILE_ERROR = 2


def read_sample(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(EXIT_FILE_ERROR)
    return p.read_text(encoding="utf-8")


GOOD_REQUIREMENTS = [
    ('标识|标注|水印', '缺少 AI 生成内容标识方案'),
    ('广告法|绝对化|FTC|披露', '缺少广告宣称核查'),
    ('(含税|VAT|价格标示)|本地化', '缺少价格标示/本地化合规'),
    ('数据|GDPR|个人信息|画像', '缺少数据与画像合规'),
    ('gotchas|坑位|红线', '缺少 gotchas 坑位引用'),
]

BAD_VIOLATIONS = [
    ('(最佳|最好|第一品牌|国家级|最高级|史上最)', '命中违规：广告绝对化用语'),
    ('(不标|隐藏|去掉).{0,6}(标识|标注|AI 生成|水印)', '命中违规：隐藏 AI 生成标识'),
    ('(不标|隐藏|去掉).{0,6}(#ad|广告|披露|赞助)', '命中违规：隐藏广告披露'),
    ('(抓取|爬).{0,8}(用户|个人).{0,4}(数据|信息).{0,8}(无需|不用|同意)', '命中违规：未经同意抓取用户数据'),
    ('(夸大|虚构).{0,6}(功效|疗效|成分)', '命中违规：夸大/虚构功效宣称'),
]


def find_violations(text: str) -> list:
    hits = []
    for pattern, msg in BAD_VIOLATIONS:
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(msg)
    return hits


def find_missing_good(text: str) -> list:
    missing = []
    for pattern, msg in GOOD_REQUIREMENTS:
        if not re.search(pattern, text, re.IGNORECASE):
            missing.append(msg)
    return missing


def main():
    if len(sys.argv) < 2:
        print("用法: validate.py <sample.md>", file=sys.stderr)
        sys.exit(EXIT_FILE_ERROR)

    sample_path = sys.argv[1]
    text = read_sample(sample_path)
    fname = Path(sample_path).name.lower()
    is_bad = "bad" in fname

    errors = []

    violations = find_violations(text)
    if is_bad:
        if not violations:
            errors.append("BAD 样例未命中任何已知违规模式（应至少命中一条）")
        else:
            errors.append(f"BAD 样例命中 {len(violations)} 条违规（预期失败）：{'; '.join(violations)}")
    else:
        if violations:
            errors.append(f"GOOD 样例命中违规（不应有）：{'; '.join(violations)}")
        missing = find_missing_good(text)
        errors.extend(missing)

    if errors:
        print(f"验证失败（{len(errors)} 项）：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    print("验证通过")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
