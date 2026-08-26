#!/usr/bin/env python3
"""Standalone deterministic oracle for one Materials AI4S V24 task.

The file is self-contained: task gold data, scoring rules, tolerances, and input
hashes are embedded at build time. It never imports or executes submission code.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import re
import statistics
import struct
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

TASK_ID = 'MS02-Q3'
REQUIRED_OUTPUTS = ['extraction.json', 'summary.json', 'report.md', 'analyze.py', 'run_log.jsonl']
MAIN_FILE = 'extraction.json'
EXPECTED_COLUMNS = []
ORACLE = json.loads('{"t_type_dict":{"T1":"Meta","T2":"Material","T3":"Property-Misc","T4":"Material","T5":"Material","T6":"Nonrecipe-Material","T7":"Operation","T8":"Operation","T9":"Operation","T10":"Operation","T11":"Operation","T12":"Operation","T13":"Operation","T14":"Operation","T15":"Operation","T16":"Operation","T17":"Operation","T18":"Operation","T19":"Operation","T20":"Operation","T21":"Operation","T22":"Operation","T23":"Operation","T24":"Operation","T25":"Operation","T26":"Operation","T27":"Operation","T28":"Operation","T29":"Operation","T30":"Material","T31":"Material","T32":"Number","T33":"Amount-Unit","T34":"Material","T35":"Material","T36":"Number","T37":"Amount-Unit","T38":"Brand","T39":"Material","T40":"Material","T41":"Reference","T42":"Characterization-Apparatus","T43":"Material","T44":"Number","T45":"Amount-Unit","T46":"Brand","T47":"Material","T49":"Number","T48":"Amount-Unit","T50":"Brand","T51":"Meta","T52":"Meta","T53":"Material","T54":"Brand","T55":"Material","T56":"Brand","T57":"Material","T58":"Brand","T59":"Synthesis-Apparatus","T60":"Material","T61":"Material","T62":"Brand","T63":"Material","T64":"Amount-Misc","T65":"Brand","T66":"Material","T67":"Number","T68":"Amount-Unit","T69":"Brand","T70":"Nonrecipe-Material","T71":"Material-Descriptor","T72":"Material-Descriptor","T73":"Nonrecipe-Material","T74":"Number","T75":"Amount-Unit","T76":"Material","T77":"Number","T78":"Amount-Unit","T79":"Brand","T80":"Material","T81":"Material","T82":"Material-Descriptor","T83":"Number","T84":"Property-Unit","T85":"Synthesis-Apparatus","T86":"Material","T87":"Meta","T88":"Material","T89":"Material-Descriptor","T90":"Material","T91":"Brand","T92":"Reference","T93":"Material","T94":"Number","T95":"Amount-Unit","T96":"Material","T97":"Material","T98":"Number","T99":"Number","T100":"Amount-Unit","T101":"Material","T102":"Number","T103":"Amount-Unit","T104":"Material","T105":"Number","T106":"Amount-Unit","T107":"Material","T108":"Number","T109":"Amount-Unit","T110":"Number","T111":"Amount-Unit","T112":"Material","T113":"Material-Descriptor","T114":"Number","T115":"Condition-Unit","T116":"Number","T117":"Condition-Unit","T118":"Number","T119":"Amount-Unit","T120":"Material","T121":"Number","T122":"Amount-Unit","T123":"Material","T124":"Material","T125":"Number","T126":"Condition-Unit","T127":"Condition-Misc","T128":"Material","T129":"Material-Descriptor","T130":"Material","T131":"Material","T132":"Material-Descriptor","T133":"Material","T134":"Material-Descriptor","T135":"Brand","T136":"Number","T137":"Number","T138":"Number","T139":"Property-Unit","T140":"Property-Type","T141":"Material","T142":"Material","T143":"Amount-Misc","T144":"Material","T145":"Synthesis-Apparatus","T146":"Number","T147":"Condition-Unit","T148":"Synthesis-Apparatus","T149":"Number","T150":"Number","T151":"Condition-Unit","T152":"Condition-Unit","T153":"Synthesis-Apparatus","T154":"Brand","T155":"Material","T156":"Number","T157":"Number","T158":"Condition-Unit","T159":"Condition-Unit","T160":"Material-Descriptor","T161":"Material","T162":"Material","T163":"Material-Descriptor","T164":"Number","T165":"Amount-Unit","T166":"Material","T167":"Condition-Type","T168":"Number","T169":"Condition-Unit","T170":"Material"},"t_span_dict":{"T1":[21,28],"T2":[29,35],"T3":[36,46],"T4":[55,84],"T5":[88,94],"T6":[109,115],"T7":[208,217],"T8":[315,326],"T9":[385,394],"T10":[466,470],"T11":[649,653],"T12":[835,839],"T13":[914,921],"T14":[1025,1033],"T15":[1153,1162],"T16":[1373,1381],"T17":[1385,1392],"T18":[1606,1615],"T19":[1641,1646],"T20":[1674,1681],"T21":[1750,1758],"T22":[1766,1776],"T23":[1914,1920],"T24":[1996,2005],"T25":[2036,2040],"T26":[2071,2078],"T27":[2129,2138],"T28":[2249,2256],"T29":[2317,2326],"T30":[126,143],"T31":[145,149],"T32":[151,153],"T33":[153,154],"T34":[160,190],"T35":[192,196],"T36":[198,200],"T37":[200,201],"T38":[223,228],"T39":[234,256],"T40":[258,309],"T41":[351,355],"T42":[398,412],"T43":[414,421],"T44":[423,428],"T45":[428,429],"T46":[431,436],"T47":[442,445],"T49":[447,449],"T48":[449,450],"T50":[452,459],"T51":[475,495],"T52":[500,515],"T53":[571,582],"T54":[584,591],"T55":[594,603],"T56":[605,610],"T57":[616,625],"T58":[627,637],"T59":[657,669],"T60":[703,731],"T61":[733,736],"T62":[738,743],"T63":[789,797],"T64":[772,788],"T65":[799,806],"T66":[812,816],"T67":[818,820],"T68":[820,821],"T69":[823,828],"T70":[871,878],"T71":[879,888],"T72":[863,870],"T73":[959,963],"T74":[964,978],"T75":[979,984],"T76":[988,992],"T77":[993,994],"T78":[995,996],"T79":[998,1003],"T80":[1010,1019],"T81":[1051,1056],"T82":[1039,1050],"T83":[1058,1060],"T84":[1061,1066],"T85":[1075,1118],"T86":[1121,1147],"T87":[1166,1178],"T88":[1211,1224],"T89":[1225,1234],"T90":[1236,1239],"T91":[1256,1288],"T92":[1329,1338],"T93":[1344,1357],"T94":[1406,1410],"T95":[1411,1412],"T96":[1413,1417],"T97":[1462,1466],"T98":[1484,1485],"T99":[1489,1491],"T100":[1491,1492],"T101":[1505,1509],"T102":[1512,1515],"T103":[1516,1517],"T104":[1518,1522],"T105":[1524,1527],"T106":[1528,1529],"T107":[1530,1535],"T108":[1540,1543],"T109":[1544,1545],"T110":[1551,1554],"T111":[1555,1556],"T112":[1557,1560],"T113":[1561,1569],"T114":[1574,1576],"T115":[1577,1581],"T116":[1586,1587],"T117":[1588,1589],"T118":[1591,1595],"T119":[1596,1597],"T120":[1601,1605],"T121":[1619,1621],"T122":[1622,1623],"T123":[1627,1631],"T124":[1655,1662],"T125":[1692,1693],"T126":[1694,1695],"T127":[1699,1715],"T128":[1717,1720],"T129":[1721,1729],"T130":[1784,1788],"T131":[1809,1816],"T132":[1817,1828],"T133":[1837,1842],"T134":[1843,1850],"T135":[1852,1859],"T136":[1864,1865],"T137":[1867,1870],"T138":[1875,1879],"T139":[1880,1882],"T140":[1883,1897],"T141":[1926,1933],"T142":[1938,1943],"T143":[1945,1964],"T144":[1968,1971],"T145":[2013,2030],"T146":[2041,2043],"T147":[2044,2045],"T148":[2057,2066],"T149":[2082,2086],"T150":[2095,2097],"T151":[2087,2090],"T152":[2098,2099],"T153":[2147,2169],"T154":[2171,2214],"T155":[2233,2238],"T156":[2261,2263],"T157":[2271,2273],"T158":[2264,2267],"T159":[2274,2278],"T160":[2221,2232],"T161":[2302,2312],"T162":[2333,2340],"T163":[2341,2349],"T164":[2361,2364],"T165":[2365,2366],"T166":[2367,2370],"T167":[2377,2396],"T168":[2401,2403],"T169":[2404,2407],"T170":[940,957]},"r_type_dict":{"R1":"Property_Of","R2":"Next_Operation","R3":"Next_Operation","R4":"Next_Operation","R5":"Next_Operation","R6":"Next_Operation","R7":"Next_Operation","R8":"Next_Operation","R9":"Next_Operation","R10":"Next_Operation","R11":"Next_Operation","R12":"Next_Operation","R13":"Next_Operation","R14":"Next_Operation","R15":"Next_Operation","R16":"Next_Operation","R17":"Next_Operation","R18":"Next_Operation","R19":"Next_Operation","R20":"Next_Operation","R21":"Next_Operation","R22":"Number_Of","R23":"Amount_Of","R24":"Coref_Of","R25":"Number_Of","R26":"Amount_Of","R27":"Coref_Of","R28":"Brand_Of","R29":"Brand_Of","R30":"Coref_Of","R31":"Apparatus_Of","R32":"Number_Of","R33":"Amount_Of","R34":"Brand_Of","R35":"Number_Of","R36":"Amount_Of","R37":"Brand_Of","R38":"Brand_Of","R39":"Brand_Of","R40":"Brand_Of","R41":"Apparatus_Of","R42":"Coref_Of","R43":"Brand_Of","R44":"Amount_Of","R46":"Brand_Of","R47":"Brand_Of","R48":"Number_Of","R49":"Amount_Of","R45":"Descriptor_Of","R50":"Descriptor_Of","R51":"Number_Of","R52":"Number_Of","R53":"Amount_Of","R54":"Brand_Of","R55":"Amount_Of","R56":"Amount_Of","R57":"Next_Operation","R58":"Descriptor_Of","R59":"Number_Of","R60":"Property_Of","R61":"Apparatus_Of","R62":"Descriptor_Of","R63":"Coref_Of","R64":"Brand_Of","R65":"Number_Of","R66":"Amount_Of","R67":"Number_Of","R68":"Number_Of","R69":"Amount_Of","R70":"Number_Of","R71":"Amount_Of","R72":"Number_Of","R73":"Amount_Of","R74":"Number_Of","R75":"Amount_Of","R76":"Number_Of","R77":"Amount_Of","R78":"Descriptor_Of","R79":"Number_Of","R80":"Number_Of","R81":"Condition_Of","R82":"Condition_Of","R83":"Number_Of","R84":"Amount_Of","R85":"Number_Of","R86":"Amount_Of","R87":"Number_Of","R88":"Condition_Of","R89":"Condition_Of","R90":"Descriptor_Of","R91":"Descriptor_Of","R92":"Descriptor_Of","R93":"Brand_Of","R94":"Number_Of","R95":"Number_Of","R96":"Number_Of","R97":"Type_Of","R98":"Property_Of","R99":"Amount_Of","R100":"Apparatus_Of","R101":"Number_Of","R102":"Condition_Of","R103":"Apparatus_Of","R104":"Number_Of","R105":"Number_Of","R106":"Condition_Of","R107":"Condition_Of","R108":"Apparatus_Of","R109":"Brand_Of","R110":"Descriptor_Of","R111":"Number_Of","R112":"Number_Of","R113":"Condition_Of","R114":"Condition_Of","R115":"Descriptor_Of","R116":"Number_Of","R117":"Amount_Of","R118":"Number_Of","R119":"Condition_Of","R120":"Type_Of"},"r_args_dict":{"R1":["T3","T2"],"R2":["E1","E2"],"R3":["E2","E3"],"R4":["E3","E4"],"R5":["E4","E5"],"R6":["E5","E6"],"R7":["E6","E7"],"R8":["E7","E8"],"R9":["E10","E11"],"R10":["E11","E12"],"R11":["E12","E13"],"R12":["E13","E14"],"R13":["E14","E15"],"R14":["E15","E16"],"R15":["E16","E17"],"R16":["E17","E18"],"R17":["E18","E19"],"R18":["E19","E20"],"R19":["E20","E21"],"R20":["E21","E22"],"R21":["E22","E23"],"R22":["T32","T33"],"R23":["T33","T30"],"R24":["T31","T30"],"R25":["T36","T37"],"R26":["T37","T34"],"R27":["T35","T34"],"R28":["T38","T34"],"R29":["T38","T30"],"R30":["T40","T39"],"R31":["T42","E3"],"R32":["T44","T45"],"R33":["T45","T43"],"R34":["T46","T43"],"R35":["T49","T48"],"R36":["T48","T47"],"R37":["T50","T47"],"R38":["T54","T53"],"R39":["T56","T55"],"R40":["T58","T57"],"R41":["T59","E5"],"R42":["T61","T60"],"R43":["T62","T60"],"R44":["T64","T63"],"R46":["T65","T63"],"R47":["T69","T66"],"R48":["T67","T68"],"R49":["T68","T66"],"R45":["T72","T70"],"R50":["T71","T70"],"R51":["T74","T75"],"R52":["T77","T78"],"R53":["T78","T76"],"R54":["T79","T76"],"R55":["T75","T73"],"R56":["T75","T170"],"R57":["E8","E9"],"R58":["T82","T81"],"R59":["T83","T84"],"R60":["T84","T81"],"R61":["T85","E8"],"R62":["T89","T88"],"R63":["T90","T88"],"R64":["T91","T88"],"R65":["T94","T95"],"R66":["T95","T96"],"R67":["T98","T100"],"R68":["T99","T100"],"R69":["T100","T97"],"R70":["T102","T103"],"R71":["T103","T104"],"R72":["T105","T106"],"R73":["T106","T107"],"R74":["T108","T109"],"R75":["T109","T112"],"R76":["T110","T111"],"R77":["T111","T112"],"R78":["T113","T112"],"R79":["T114","T115"],"R80":["T116","T117"],"R81":["T115","E11"],"R82":["T117","E11"],"R83":["T118","T119"],"R84":["T119","T120"],"R85":["T121","T122"],"R86":["T122","T123"],"R87":["T125","T126"],"R88":["T126","E14"],"R89":["T127","E14"],"R90":["T129","T128"],"R91":["T132","T131"],"R92":["T134","T133"],"R93":["T135","T133"],"R94":["T137","T139"],"R95":["T138","T139"],"R96":["T136","T139"],"R97":["T140","T139"],"R98":["T139","T133"],"R99":["T143","T144"],"R100":["T145","E18"],"R101":["T146","T147"],"R102":["T147","E19"],"R103":["T148","E20"],"R104":["T149","T151"],"R105":["T150","T152"],"R106":["T151","E20"],"R107":["T152","E20"],"R108":["T153","E21"],"R109":["T154","T153"],"R110":["T160","T155"],"R111":["T156","T158"],"R112":["T157","T159"],"R113":["T158","E22"],"R114":["T159","E22"],"R115":["T163","T162"],"R116":["T164","T165"],"R117":["T165","T166"],"R118":["T168","T169"],"R119":["T169","E23"],"R120":["T167","T169"]},"e_type_dict":{"E1":"Operation","E2":"Operation","E3":"Operation","E4":"Operation","E5":"Operation","E6":"Operation","E7":"Operation","E8":"Operation","E9":"Operation","E10":"Operation","E11":"Operation","E12":"Operation","E13":"Operation","E14":"Operation","E15":"Operation","E16":"Operation","E17":"Operation","E18":"Operation","E19":"Operation","E20":"Operation","E21":"Operation","E22":"Operation","E23":"Operation"},"e_trig_dict":{"E1":"T7","E2":"T8","E3":"T9","E4":"T10","E5":"T11","E6":"T12","E7":"T13","E8":"T14","E9":"T15","E10":"T16","E11":"T17","E12":"T18","E13":"T19","E14":"T20","E15":"T21","E16":"T22","E17":"T23","E18":"T24","E19":"T25","E20":"T26","E21":"T27","E22":"T28","E23":"T29"},"e_args_dict":{"E1":[["Recipe_Precursor","T34"],["Recipe_Precursor","T30"]],"E2":[["Recipe_Target","T39"]],"E3":[],"E4":[["Solvent_Material","T47"],["Solvent_Material","T43"]],"E5":[["Participant_Material","T57"],["Participant_Material","T55"],["Participant_Material","T53"],["Participant_Material","T60"]],"E6":[["Participant_Material","T70"]],"E7":[["Participant_Material","T170"]],"E8":[["Participant_Material","T80"],["Solvent_Material","T81"]],"E9":[["Recipe_Target","T86"],["Participant_Material","T88"]],"E10":[["Participant_Material","T93"]],"E11":[["Recipe_Precursor","T96"],["Solvent_Material","T104"],["Solvent_Material","T107"],["Solvent_Material","T112"]],"E12":[["Participant_Material","T120"],["Solvent_Material","T123"]],"E13":[["Participant_Material","T124"]],"E14":[],"E15":[["Participant_Material","T128"]],"E16":[["Participant_Material","T130"],["Participant_Material","T131"],["Participant_Material","T133"]],"E17":[["Solvent_Material","T141"],["Solvent_Material","T142"]],"E18":[["Participant_Material","T144"]],"E19":[],"E20":[],"E21":[],"E22":[["Participant_Material","T155"]],"E23":[["Participant_Material","T161"],["Solvent_Material","T162"],["Solvent_Material","T166"]]}}')
SCORING_SPEC = json.loads('{"type":"structured_ie","span_match":"exact","micro_f1":true}')
INPUT_MANIFEST = json.loads('{"question_id":"MS02-Q3","files":[{"path":"inputs/label_schema.json","bytes":900,"sha256":"31204FAC16486E10C91076E825F7F124D743E2966E4375D7150E6016906FA155"},{"path":"inputs/procedure.txt","bytes":2501,"sha256":"15306E0C80C33A52ED4DA0642EBD682E518F4ED0A3BFF6F0E53A1B19D71DCC11"},{"path":"inputs/source_manifest.json","bytes":733,"sha256":"B160FFC0069DCB4CBA351851753F6270ED6AA1328C234075822FC70A677BEDA2"}]}')
EMBEDDED_ORACLE_SHA256 = 'AAD8E4D5F20654B4110F7C940A2CAC2569641F55A07260860A0198FB20CF98F0'
DERIVED_GOLD = json.loads('{}')
MANUAL_TASKS = set()
MANUAL_ANCHORS = json.loads('{}')
REGRESSION_CONFIG = json.loads('{}')
CRITERIA_LAYOUT = [('实体 span/type F1', 30), ('关系 F1', 15), ('事件 trigger/argument F1', 20), ('offset 与 schema', 10), ('报告', 5)]

GRADER_VERSION = "v24-standalone-oracle-1.0"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def truthy(value: Any) -> bool:
    return str(value).strip().casefold() in {"1", "true", "yes", "y", "eligible", "valid", "ok"}


def norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def flatten_strings(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for child in value.values():
            result.extend(flatten_strings(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(flatten_strings(child))
    elif value is not None:
        result.append(str(value))
    return result


def reject_nonfinite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite JSON number")
    if isinstance(value, dict):
        for child in value.values():
            reject_nonfinite(child)
    elif isinstance(value, list):
        for child in value:
            reject_nonfinite(child)


def parse_artifact(path: Path) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("missing or empty")
    suffix = path.suffix.casefold()
    if suffix == ".json":
        reject_nonfinite(read_json(path))
    elif suffix == ".jsonl":
        lines = [line for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        if not lines:
            raise ValueError("empty jsonl")
        for line in lines:
            reject_nonfinite(json.loads(line))
    elif suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            if not reader.fieldnames:
                raise ValueError("missing header")
            list(reader)
    elif suffix == ".png":
        if not valid_png(path):
            raise ValueError("invalid PNG")
    elif suffix == ".py":
        ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
    else:
        path.read_text(encoding="utf-8")


def valid_png(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 33:
        return False
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        return False
    width, height = struct.unpack(">II", data[16:24])
    return width > 0 and height > 0 and data[-12:] == b"\x00\x00\x00\x00IEND\xaeB`\x82"


def criterion(name: str, maximum: float, metric: float, detail: str = "") -> dict[str, Any]:
    metric = max(0.0, min(1.0, float(metric)))
    return {
        "name": name,
        "points": maximum * metric,
        "max_points": float(maximum),
        "metric": metric,
        "detail": detail,
    }


def exact(name: str, maximum: float, correct: int, total: int, detail: str = "") -> dict[str, Any]:
    metric = correct / total if total else 0.0
    return criterion(name, maximum, metric, detail or f"{correct}/{total}")


def set_f1(predicted: set[Any], gold: set[Any]) -> tuple[float, int, int, int]:
    tp = len(predicted & gold)
    denominator = len(predicted) + len(gold)
    return (2 * tp / denominator if denominator else 1.0), tp, len(predicted), len(gold)


def classification_metrics(gold: list[Any], pred: list[Any]) -> tuple[float, float]:
    labels = sorted(set(gold) | set(pred), key=str)
    recalls: list[float] = []
    f1s: list[float] = []
    for label in labels:
        tp = sum(g == label and p == label for g, p in zip(gold, pred))
        fp = sum(g != label and p == label for g, p in zip(gold, pred))
        fn = sum(g == label and p != label for g, p in zip(gold, pred))
        recalls.append(tp / (tp + fn) if tp + fn else 0.0)
        f1s.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
    return (sum(recalls) / len(recalls), sum(f1s) / len(f1s)) if labels else (0.0, 0.0)


def macro_f1(gold: list[Any], pred: list[Any]) -> float:
    return classification_metrics(gold, pred)[1]


def non_o_micro_f1(gold: list[str], pred: list[str]) -> float:
    tp = sum(g == p and g != "O" for g, p in zip(gold, pred))
    fp = sum(p != "O" and p != g for g, p in zip(gold, pred))
    fn = sum(g != "O" and p != g for g, p in zip(gold, pred))
    return 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0


def regression_metrics(gold: list[float], pred: list[float], baseline: float) -> dict[str, float]:
    mae = sum(abs(a - b) for a, b in zip(gold, pred)) / len(gold)
    rmse = math.sqrt(sum((a - b) ** 2 for a, b in zip(gold, pred)) / len(gold))
    baseline_mae = sum(abs(a - baseline) for a in gold) / len(gold)
    mean_gold = sum(gold) / len(gold)
    denominator = sum((a - mean_gold) ** 2 for a in gold)
    r2 = 1.0 - sum((a - b) ** 2 for a, b in zip(gold, pred)) / denominator if denominator else 0.0
    return {
        "mae": mae,
        "rmse": rmse,
        "baseline_mae": baseline_mae,
        "mae_improvement": max(0.0, min(1.0, 1.0 - mae / baseline_mae)) if baseline_mae else 0.0,
        "r2": r2,
        "r2_clipped": max(0.0, min(1.0, r2)),
    }


def linear_quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    low = int(math.floor(position))
    high = int(math.ceil(position))
    if low == high:
        return ordered[low]
    fraction = position - low
    return ordered[low] * (1 - fraction) + ordered[high] * fraction


def formula_counts(formula: str) -> dict[str, float] | None:
    counts: Counter[str] = Counter()
    for element, number in re.findall(r"([A-Z][a-z]?)([0-9.]*)", str(formula)):
        counts[element] += float(number) if number else 1.0
    if not counts:
        return None
    scale = min(value for value in counts.values() if value > 0)
    return {key: round(value / scale, 8) for key, value in sorted(counts.items())}


def report_criterion(output: Path, maximum: float = 5) -> dict[str, Any]:
    path = output / "report.md"
    if not path.is_file():
        return criterion("报告", maximum, 0, "report.md missing")
    text = path.read_text(encoding="utf-8-sig").strip()
    checks = [bool(text), len(text) <= 300]
    return exact("报告", maximum, sum(checks), len(checks), f"nonempty={checks[0]}, chars={len(text)}")


def script_criterion(output: Path, maximum: float) -> tuple[dict[str, Any], list[str]]:
    path = output / "analyze.py"
    checks: list[bool] = []
    failures: list[str] = []
    if not path.is_file():
        return criterion("复现", maximum, 0, "analyze.py missing"), ["SCRIPT_MISSING"]
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename="analyze.py")
        checks.append(True)
        literals = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
        forbidden = any(
            value.startswith(("C:\\", "/Users/", "/home/"))
            or re.search(r"(?:private|oracle|gold|answer|scoring_spec)", value, re.I)
            for value in literals
        )
        checks.append(not forbidden)
        if forbidden:
            failures.append("SCRIPT_FORBIDDEN_REFERENCE")
    except Exception as exc:
        checks.extend([False, False])
        failures.append(f"SCRIPT_SYNTAX:{type(exc).__name__}")
    log_path = output / "run_log.jsonl"
    try:
        parse_artifact(log_path)
        checks.append(True)
    except Exception:
        checks.append(False)
        failures.append("RUN_LOG_INVALID")
    return exact("复现", maximum, sum(checks), len(checks), "static syntax/path/log checks"), failures


def plot_criterion(output: Path, filename: str, maximum: float) -> dict[str, Any]:
    ok = valid_png(output / filename)
    return exact("科研图", maximum, int(ok), 1, f"valid PNG={ok}")


def verify_inputs(workspace: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for record in INPUT_MANIFEST["files"]:
        path = workspace / record["path"]
        if not path.is_file():
            failures.append(f"HG_INPUT_MISSING:{record['path']}")
        elif path.stat().st_size != int(record["bytes"]):
            failures.append(f"HG_INPUT_SIZE:{record['path']}")
        elif sha256_file(path) != record["sha256"].upper():
            failures.append(f"HG_INPUT_HASH:{record['path']}")
    return not failures, failures


def required_artifacts(output: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for name in REQUIRED_OUTPUTS:
        path = output / name
        if not path.is_file():
            failures.append(f"HG_DELIVERABLE_MISSING:{name}")
            continue
        try:
            parse_artifact(path)
        except Exception as exc:
            failures.append(f"HG_DELIVERABLE_INVALID:{name}:{type(exc).__name__}")
    return not failures, failures


def main_csv(workspace: Path) -> tuple[list[dict[str, str]], list[str]]:
    path = workspace / "output" / MAIN_FILE
    if not path.is_file():
        return [], [f"HG_MAIN_MISSING:{MAIN_FILE}"]
    try:
        header, rows = read_csv(path)
    except Exception as exc:
        return [], [f"HG_MAIN_INVALID:{type(exc).__name__}"]
    failures: list[str] = []
    if EXPECTED_COLUMNS and header != EXPECTED_COLUMNS:
        failures.append(f"HG_SCHEMA:{header!r}")
    return rows, failures


def anchor_variants(anchor: Any) -> list[str]:
    values = anchor if isinstance(anchor, list) else [anchor]
    return [norm(value) for value in values if norm(value)]


def anchor_match(anchor: Any, text: str) -> bool:
    normalized = norm(text)
    return any(value in normalized for value in anchor_variants(anchor))


def predicted_numbers(value: Any, parent_key: str = "") -> list[str]:
    if parent_key.casefold() in {"id", "step_id", "index", "order", "rank", "case_id"}:
        return []
    result: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            result.extend(predicted_numbers(child, str(key)))
    elif isinstance(value, list):
        for child in value:
            result.extend(predicted_numbers(child, parent_key))
    elif value is not None:
        result.extend(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", str(value)))
    return result


def manual_material_items(payload: Any) -> list[str]:
    if isinstance(payload, dict):
        for key in ("materials", "raw_materials", "ingredients", "precursors"):
            if isinstance(payload.get(key), list):
                return [" ".join(flatten_strings(item)) for item in payload[key]]
    if isinstance(payload, list):
        return [" ".join(flatten_strings(item)) for item in payload]
    return []


def score_manual(workspace: Path) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    output = workspace / "output"
    payload = read_json(output / MAIN_FILE)
    reference = MANUAL_ANCHORS
    all_text = " ".join(flatten_strings(payload))
    public_text = " ".join(
        path.read_text(encoding="utf-8-sig", errors="replace")
        for path in (workspace / "inputs").iterdir()
        if path.is_file() and path.suffix.casefold() in {".json", ".txt", ".csv"}
    )
    criteria: list[dict[str, Any]] = []
    failures: list[str] = []
    metrics: dict[str, Any] = {}

    if reference["mode"] in {"materials", "materials_stage"}:
        items = manual_material_items(payload)
        predicted_hits = {i for i, anchor in enumerate(reference["entities"]) if anchor_match(anchor, all_text)}
        predicted_item_matches = sum(any(anchor_match(anchor, item) for anchor in reference["entities"]) for item in items)
        precision_denominator = max(len(items), len(predicted_hits))
        precision = predicted_item_matches / precision_denominator if precision_denominator else 0.0
        recall = len(predicted_hits) / len(reference["entities"])
        entity_f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        criteria.append(criterion("原料实体 F1", reference["weights"][0], entity_f1, f"precision={precision:.6f}, recall={recall:.6f}"))
        role_checks = []
        for entry in reference.get("roles", []):
            role_checks.append(any(anchor_match(entry["entity"], item) and anchor_match(entry["role"], item) for item in items))
        criteria.append(exact("角色 F1", reference["weights"][1], sum(role_checks), len(role_checks), "entity and role co-occur in one material item"))
        if reference["mode"] == "materials_stage":
            stage_checks = []
            for entry in reference.get("stages", []):
                stage_checks.append(any(anchor_match(entry["entity"], item) and anchor_match(entry["stage"], item) for item in items))
            criteria.append(exact("步骤归属", reference["weights"][2], sum(stage_checks), len(stage_checks)))
            restraint_weight = reference["weights"][3]
            format_weight = 0
        else:
            restraint_weight = reference["weights"][2]
            format_weight = reference["weights"][3]
        public_nums = set(predicted_numbers(public_text))
        output_nums = predicted_numbers(payload)
        unsupported = [value for value in output_nums if value not in public_nums]
        restraint = 1.0 - len(unsupported) / max(len(output_nums), 1)
        criteria.append(criterion("缺参克制", restraint_weight, restraint, f"unsupported_numbers={unsupported[:10]}"))
        if format_weight:
            case = read_json(workspace / "inputs" / "case.json")
            schema_checks = [isinstance(payload, dict), bool(items), str(payload.get("case_id", payload.get("id", ""))) in {"", str(case.get("id", ""))}]
            criteria.append(exact("格式与覆盖", format_weight, sum(schema_checks), len(schema_checks)))
        metrics.update({"entity_f1": entity_f1, "unsupported_number_count": len(unsupported)})

    elif reference["mode"] == "procedure":
        steps = payload.get("steps", []) if isinstance(payload, dict) else []
        step_texts = [" ".join(flatten_strings(step)) for step in steps]
        positions: list[int | None] = []
        for anchor in reference["actions"]:
            positions.append(next((index for index, text in enumerate(step_texts) if anchor_match(anchor, text)), None))
        recall = sum(position is not None for position in positions) / len(positions)
        action_weight, order_weight, entity_weight, restraint_weight, format_weight = reference["weights"]
        criteria.append(criterion("关键步骤覆盖", action_weight, recall, f"matched={sum(p is not None for p in positions)}/{len(positions)}"))
        pairs = [(a, b) for a in range(len(positions)) for b in range(a + 1, len(positions)) if positions[a] is not None and positions[b] is not None]
        order_ok = sum(positions[a] < positions[b] for a, b in pairs)
        criteria.append(exact("顺序一致性", order_weight, order_ok, len(pairs), "pairwise order among matched anchors"))
        entity_hits = sum(anchor_match(anchor, all_text) for anchor in reference["entities"])
        criteria.append(exact("材料/条件实体", entity_weight, entity_hits, len(reference["entities"])))
        public_nums = set(predicted_numbers(public_text))
        output_nums = predicted_numbers(payload)
        unsupported = [value for value in output_nums if value not in public_nums]
        restraint = 1.0 - len(unsupported) / max(len(output_nums), 1)
        criteria.append(criterion("缺参克制", restraint_weight, restraint, f"unsupported_numbers={unsupported[:10]}"))
        schema_checks = [isinstance(payload, dict), isinstance(steps, list), bool(steps), len(step_texts) == len(steps)]
        criteria.append(exact("复现与格式", format_weight, sum(schema_checks), len(schema_checks)))
        metrics.update({"action_recall": recall, "pairwise_order_accuracy": order_ok / len(pairs) if pairs else 0.0, "unsupported_number_count": len(unsupported)})

    else:  # characterization
        methods = sum(anchor_match(anchor, all_text) for anchor in reference["methods"])
        conclusions = sum(anchor_match(anchor, all_text) for anchor in reference["conclusions"])
        method_weight, conclusion_weight, separation_weight, format_weight = reference["weights"]
        criteria.append(exact("表征项目召回", method_weight, methods, len(reference["methods"])))
        criteria.append(exact("定性结论一致性", conclusion_weight, conclusions, len(reference["conclusions"])))
        lower = all_text.casefold()
        separation_terms = ["predict", "expected", "inferred", "hypothesis", "待验证", "预测", "推断"]
        separation = sum(term in lower for term in separation_terms)
        criteria.append(criterion("事实/预测分层", separation_weight, 1.0 if separation else 0.0, "prediction boundary markers"))
        criteria.append(criterion("覆盖与格式", format_weight, 1.0 if isinstance(payload, dict) and payload else 0.0))
        metrics.update({"method_recall": methods / len(reference["methods"]), "conclusion_recall": conclusions / len(reference["conclusions"])})

    criteria.append(report_criterion(output, 5))
    if sum(item["max_points"] for item in criteria) != 80:
        raise ValueError("manual criteria do not sum to 80")
    return criteria, failures, metrics


def ie_entity_signature(entity: dict[str, Any]) -> tuple[int, int, str]:
    return int(entity["start"]), int(entity["end"]), norm(entity["type"])


def extract_bio_entities(rows: list[dict[str, Any]], label_key: str) -> set[tuple[str, int, int, str]]:
    result: set[tuple[str, int, int, str]] = set()
    current: tuple[str, int, int, str] | None = None
    for row in rows:
        sid = str(row["sentence_id"])
        tid = int(row["token_id"])
        label = str(row.get(label_key, ""))
        if label == "O" or not label:
            if current:
                result.add(current)
                current = None
            continue
        prefix, kind = label.split("-", 1) if "-" in label else ("B", label)
        if prefix == "B" or current is None or current[0] != sid or current[3] != norm(kind) or tid != current[2] + 1:
            if current:
                result.add(current)
            current = (sid, tid, tid, norm(kind))
        else:
            current = (current[0], current[1], tid, current[3])
    if current:
        result.add(current)
    return result


def score_task(workspace: Path) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    output = workspace / "output"
    qid = TASK_ID
    failures: list[str] = []
    metrics: dict[str, Any] = {}

    if qid in MANUAL_TASKS:
        return score_manual(workspace)

    rows, schema_failures = main_csv(workspace) if MAIN_FILE.endswith(".csv") else ([], [])
    failures.extend(schema_failures)

    if qid == "MS01-Q1":
        gold = set(ORACLE["eligible_ids"])
        candidates = read_csv(workspace / "inputs" / "candidates.csv")[1]
        expected_ids = [row["material_id"] for row in candidates]
        by_id = {row.get("material_id", ""): row for row in rows}
        correct = sum(mid in by_id and truthy(by_id[mid].get("eligible")) == (mid in gold) for mid in expected_ids)
        ranked = sorted((row for row in rows if str(row.get("rank", "")).strip()), key=lambda row: int(float(row["rank"])))
        top = [row["material_id"] for row in ranked[:20]]
        rank_correct = sum(a == b for a, b in zip(top, ORACLE["top20"]))
        format_checks = [set(by_id) == set(expected_ids), len(by_id) == len(rows), not schema_failures]
        script, script_failures = script_criterion(output, 5)
        failures.extend(script_failures)
        criteria = [exact("硬约束判定", 40, correct, len(expected_ids)), exact("Top-k 排序", 20, rank_correct, 20), exact("格式与覆盖", 10, sum(format_checks), len(format_checks)), script, report_criterion(output)]
        if correct != len(expected_ids): failures.append("HG_HARD_CONSTRAINT_MISMATCH")
        if not all(format_checks): failures.append("HG_ID_COVERAGE")
        metrics.update({"eligibility_accuracy": correct / len(expected_ids), "top20_position_accuracy": rank_correct / 20})

    elif qid == "MS01-Q2":
        gold_rows = {row["jid"]: row for row in ORACLE["rows"]}
        pred = {row.get("jid", ""): row for row in rows}
        class_ok = sum(pred.get(jid, {}).get("stability_class") == gold["stability_class"] for jid, gold in gold_rows.items())
        ranked = [row["jid"] for row in sorted(rows, key=lambda row: int(float(row["rank"]))) if row.get("rank")]
        rank_ok = sum(a == b for a, b in zip(ranked, ORACLE["ranked_ids"]))
        summary = read_json(output / "summary.json")
        expected_counts = Counter(row["stability_class"] for row in ORACLE["rows"])
        flat_summary = flatten_strings(summary)
        count_ok = sum(str(value) in flat_summary for value in expected_counts.values())
        script, sf = script_criterion(output, 5); failures.extend(sf)
        criteria = [exact("稳定性分级", 35, class_ok, len(gold_rows)), exact("全量排名", 25, rank_ok, len(ORACLE["ranked_ids"])), exact("汇总", 10, count_ok, len(expected_counts)), script, report_criterion(output)]
        if set(pred) != set(gold_rows): failures.append("HG_ID_COVERAGE")
        metrics.update({"classification_accuracy": class_ok / len(gold_rows), "rank_position_accuracy": rank_ok / len(ORACLE["ranked_ids"])})

    elif qid == "MS01-Q3":
        pred = {str(row.get("sample_id", "")): row for row in rows}
        gold_rows = ORACLE["test_labels"]
        ids = [str(row["sample_id"]) for row in gold_rows]
        gold = [int(row["gfa"]) for row in gold_rows]
        predicted = [int(float(pred.get(sid, {}).get("gfa_pred", -99))) for sid in ids]
        ba, mf1 = classification_metrics(gold, predicted)
        coverage = sum(sid in pred and finite(pred[sid].get("gfa_probability")) and 0 <= float(pred[sid]["gfa_probability"]) <= 1 for sid in ids)
        cv = read_json(output / "cv_metrics.json")
        protocol = [int(cv.get("n_splits", 0)) == 5, cv.get("seed") is not None, "strat" in str(cv.get("splitter", "")).casefold()]
        script, sf = script_criterion(output, 5); failures.extend(sf)
        criteria = [criterion("隐藏测试 balanced accuracy", 30, ba), criterion("隐藏测试 macro-F1", 20, mf1), exact("概率与覆盖", 10, coverage, len(ids)), exact("交叉验证协议", 10, sum(protocol), len(protocol)), script, report_criterion(output)]
        if coverage != len(ids) or len(rows) != len(ids) or len(pred) != len(ids): failures.append("HG_ID_OR_PROBABILITY")
        metrics.update({"balanced_accuracy": ba, "macro_f1": mf1})

    elif qid == "MS02-Q3":
        payload = read_json(output / "extraction.json")
        gold_entities = {(int(ORACLE["t_span_dict"][key][0]), int(ORACLE["t_span_dict"][key][1]), norm(ORACLE["t_type_dict"][key])) for key in ORACLE["t_type_dict"]}
        pred_entities = {ie_entity_signature(entity) for entity in payload.get("entities", [])}
        ef1, etp, ep, eg = set_f1(pred_entities, gold_entities)
        pred_by_id = {entity["id"]: ie_entity_signature(entity) for entity in payload.get("entities", [])}
        gold_t = {key: (int(ORACLE["t_span_dict"][key][0]), int(ORACLE["t_span_dict"][key][1]), norm(ORACLE["t_type_dict"][key])) for key in ORACLE["t_type_dict"]}
        gold_event_node = {key: ("event", norm(ORACLE["e_type_dict"][key]), gold_t[ORACLE["e_trig_dict"][key]]) for key in ORACLE["e_type_dict"]}
        def gold_node(node: str) -> Any:
            return gold_t[node] if node.startswith("T") else gold_event_node.get(node, ("unknown", node))
        gold_rel = {(norm(ORACLE["r_type_dict"][key]), gold_node(ORACLE["r_args_dict"][key][0]), gold_node(ORACLE["r_args_dict"][key][1])) for key in ORACLE["r_type_dict"]}
        pred_rel = {(norm(rel["type"]), pred_by_id.get(rel["head"], ("missing", rel["head"])), pred_by_id.get(rel["tail"], ("missing", rel["tail"]))) for rel in payload.get("relations", [])}
        rf1, rtp, rp, rg = set_f1(pred_rel, gold_rel)
        gold_events = set()
        for key in ORACLE["e_type_dict"]:
            args = tuple(sorted((norm(role), gold_t[target]) for role, target in ORACLE["e_args_dict"][key]))
            gold_events.add((norm(ORACLE["e_type_dict"][key]), gold_t[ORACLE["e_trig_dict"][key]], args))
        pred_events = set()
        for event in payload.get("events", []):
            args = tuple(sorted((norm(arg["role"]), pred_by_id.get(arg["entity_id"], ("missing", arg["entity_id"]))) for arg in event.get("arguments", [])))
            pred_events.add((norm(event["type"]), pred_by_id.get(event["trigger"], ("missing", event["trigger"])), args))
        vf1, vtp, vp, vg = set_f1(pred_events, gold_events)
        text = (workspace / "inputs" / "procedure.txt").read_text(encoding="utf-8")
        entities = payload.get("entities", [])
        valid = sum(0 <= int(entity["start"]) < int(entity["end"]) <= len(text) and text[int(entity["start"]):int(entity["end"])] == entity.get("text") for entity in entities)
        schema = [valid == len(entities), len(pred_by_id) == len(entities), all(rel.get("head") in pred_by_id and rel.get("tail") in pred_by_id for rel in payload.get("relations", [])), all(event.get("trigger") in pred_by_id and all(arg.get("entity_id") in pred_by_id for arg in event.get("arguments", [])) for event in payload.get("events", []))]
        criteria = [criterion("实体 span/type F1", 30, ef1), criterion("关系 F1", 15, rf1), criterion("事件 trigger/argument F1", 20, vf1), exact("offset 与 schema", 10, sum(schema), len(schema)), report_criterion(output)]
        if not all(schema): failures.append("HG_OFFSET_OR_SCHEMA")
        metrics.update({"entity_f1": ef1, "relation_f1": rf1, "event_f1": vf1, "entity_tp": etp, "relation_tp": rtp, "event_tp": vtp})

    elif qid == "MS03-Q1":
        pred = {row.get("sample_id", ""): row for row in rows}
        labels = ORACLE["test_labels"]
        correct = sum(str(pred.get(row["sample_id"], {}).get("space_group_number")) == str(row["space_group_number"]) and pred.get(row["sample_id"], {}).get("space_group_symbol") == row["space_group_symbol"] for row in labels)
        peaks_header, peaks_rows = read_csv(output / "peaks.csv")
        expected = {(row["sample_id"], str(row["point_id"])): row for row in DERIVED_GOLD["peaks"]}
        actual = {(row.get("sample_id", ""), str(int(float(row.get("point_id", -1))))): row for row in peaks_rows}
        union = set(expected) | set(actual)
        peak_ok = 0
        for key in union:
            if key in expected and key in actual:
                peak_ok += all(finite(actual[key].get(field)) and abs(float(actual[key][field]) - float(expected[key][field])) <= 1e-6 for field in ("x", "intensity", "relative_intensity"))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("空间群准确率", 35, correct, len(labels)), exact("峰位与强度", 20, peak_ok, len(union)), plot_criterion(output, "patterns.png", 10), script, report_criterion(output)]
        if set(pred) != {row["sample_id"] for row in labels}: failures.append("HG_ID_COVERAGE")
        metrics.update({"space_group_accuracy": correct / len(labels), "peak_exact_accuracy": peak_ok / len(union) if union else 0})

    elif qid == "MS03-Q2":
        pred = {(str(row.get("sentence_id", "")), str(row.get("token_id", ""))): row.get("tag", "") for row in rows}
        gold_rows = ORACLE["test_tags"]
        keys = [(str(row["sentence_id"]), str(row["token_id"])) for row in gold_rows]
        gold = [row["tag"] for row in gold_rows]
        predicted = [pred.get(key, "__MISSING__") for key in keys]
        mf1 = macro_f1(gold, predicted); nono = non_o_micro_f1(gold, predicted)
        coverage = sum(key in pred for key in keys)
        cv = read_json(output / "cv_metrics.json")
        protocol = [int(cv.get("n_splits", 0)) == 5, "groupkfold" in str(cv.get("splitter", "")).casefold(), "sentence" in str(cv.get("splitter", "")).casefold()]
        criteria = [criterion("token macro-F1", 35, mf1), criterion("非 O micro-F1", 20, nono), exact("覆盖与对齐", 10, coverage, len(keys)), exact("验证协议", 10, sum(protocol), len(protocol)), report_criterion(output)]
        if coverage != len(keys) or len(pred) != len(keys): failures.append("HG_TOKEN_ALIGNMENT")
        metrics.update({"macro_f1": mf1, "non_o_micro_f1": nono})

    elif qid == "MS03-Q3":
        by = {row.get("feature", ""): row for row in rows}
        features = ["n_sites", "volume_a3"]
        corr = sum(feature in by and finite(by[feature].get("pearson_r")) and abs(float(by[feature]["pearson_r"]) - float(ORACLE[f"pearson_{'volume' if feature == 'volume_a3' else 'n_sites'}"])) <= 1e-6 for feature in features)
        ci_ok = 0
        for feature in features:
            expected = DERIVED_GOLD["bootstrap_ci"][feature]
            row = by.get(feature, {})
            ci_ok += finite(row.get("ci_low")) and abs(float(row["ci_low"]) - expected[0]) <= 1e-6
            ci_ok += finite(row.get("ci_high")) and abs(float(row["ci_high"]) - expected[1]) <= 1e-6
        summary = read_json(output / "summary.json")
        audit = [all(feature in by for feature in features), all(int(float(by[feature].get("n", -1))) == int(ORACLE["n"]) for feature in features if feature in by), bool(summary), all(finite(by[feature].get(field)) for feature in features if feature in by for field in ("pearson_r", "spearman_rho", "ci_low", "ci_high"))]
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("相关系数", 30, corr, 2), exact("bootstrap 区间", 15, ci_ok, 4), exact("数据审计", 10, sum(audit), len(audit)), plot_criterion(output, "association.png", 10), script, report_criterion(output)]
        if not all(audit): failures.append("HG_DATA_AUDIT")
        metrics.update({"pearson_checks": corr, "bootstrap_ci_checks": ci_ok})

    elif qid == "MS04-Q1":
        pred = {row.get("structure", "").replace("_pred.cif", ""): row for row in rows}
        fields = ["wyckoff_rmse", "wyckoff_mae", "sinkhorn_dist", "chamfer_dist", "hausdorff_dist", "superpose_rmsd", "edit_graph_distance", "fingerPrint", "XRD_dist", "OFM_dist"]
        correct = 0
        for gold in ORACLE["distance_rows"]:
            key = gold["structure"].replace("_pred.cif", "")
            row = pred.get(key, {})
            try:
                status_map = json.loads(row.get("status", "{}"))
            except (TypeError, ValueError, json.JSONDecodeError):
                status_map = {}
            for field in fields:
                gv, pv = gold.get(field), row.get(field)
                if finite(gv):
                    correct += finite(pv) and abs(float(gv) - float(pv)) <= 1e-4
                else:
                    # Official CSPBenchMetrics may mark dependency-bound metrics
                    # unavailable. A blank value with an explicit per-field status
                    # is the exact expected representation; fabricated zero is not.
                    correct += not finite(pv) and bool(str(status_map.get(field, "")).strip())
        coverage = []
        for key in ("SrTiO3", "GdB2"):
            row = pred.get(key, {})
            try:
                status_map = json.loads(row.get("status", "{}"))
            except (TypeError, ValueError, json.JSONDecodeError):
                status_map = {}
            coverage.append(key in pred and all(field in row for field in fields) and all(field in status_map for field in fields))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("官方距离复现", 55, correct, len(fields) * 2), exact("状态与覆盖", 10, sum(coverage), len(coverage)), script, report_criterion(output)]
        if not all(coverage): failures.append("HG_DISTANCE_STATUS_OR_COVERAGE")
        metrics.update({"distance_field_accuracy": correct / (len(fields) * 2)})

    elif qid == "MS04-Q2":
        pred = {(row.get("algorithm", ""), row.get("formula", "")): row for row in rows}
        coverage_gold = ORACLE["coverage"]
        coverage_ok = sum((gold["algorithm"], gold["formula"]) in pred and truthy(pred[(gold["algorithm"], gold["formula"])].get("present")) == bool(gold["file_present"]) for gold in coverage_gold)
        audit_checks: list[bool] = []
        for gold in coverage_gold:
            row = pred.get((gold["algorithm"], gold["formula"]), {})
            audit_checks.extend([bool(row.get("path")), str(row.get("parseable", "")).casefold() in {"true", "false"}, str(row.get("formula_match", "")).casefold() in {"true", "false"}])
        _, summaries = read_csv(output / "algorithm_summary.csv")
        sum_checks: list[bool] = []
        for summary in summaries:
            group = [row for row in rows if row.get("algorithm") == summary.get("algorithm")]
            sum_checks.extend([int(float(summary.get("denominator", -1))) == 23, int(float(summary.get("present_count", summary.get("present", -1)))) == sum(truthy(row.get("present")) for row in group), int(float(summary.get("parseable_count", summary.get("parseable", -1)))) == sum(truthy(row.get("parseable")) for row in group), int(float(summary.get("formula_match_count", summary.get("formula_match", -1)))) == sum(truthy(row.get("formula_match")) for row in group)])
        script, sf = script_criterion(output, 5); failures.extend(sf)
        criteria = [exact("覆盖矩阵", 30, coverage_ok, int(ORACLE["expected_rows"])), exact("CIF 质检", 25, sum(audit_checks), len(audit_checks)), exact("算法汇总", 15, sum(sum_checks), len(sum_checks)), script, report_criterion(output)]
        if coverage_ok != int(ORACLE["expected_rows"]) or len(rows) != int(ORACLE["expected_rows"]): failures.append("HG_FIXED_DENOMINATOR_OR_COVERAGE")
        metrics.update({"coverage_accuracy": coverage_ok / int(ORACLE["expected_rows"])})

    elif qid == "MS04-Q3":
        pred = {row.get("material_id", ""): row for row in rows}
        parse_checks: list[bool] = []; error_checks: list[bool] = []; cif_checks: list[bool] = []
        for gold in ORACLE["rows"]:
            row = pred.get(gold["material_id"], {})
            parse_checks.extend([formula_counts(row.get("formula_from_sites", "")) == formula_counts(gold["formula_from_sites"]), str(row.get("n_sites")) == str(gold["n_sites"]), finite(row.get("structure_volume_a3")) and abs(float(row["structure_volume_a3"]) - float(gold["volume_a3"])) <= 1e-6])
            error_checks.extend([finite(row.get("record_volume_a3")) and abs(float(row["record_volume_a3"]) - float(gold["record_volume"])) <= 1e-6, finite(row.get("volume_abs_error")) and abs(float(row["volume_abs_error"]) - float(gold["volume_abs_error"])) <= 1e-6])
            cif_checks.extend([truthy(row.get("cif_parseable")), not str(row.get("issue_codes", "")).strip()])
        script, sf = script_criterion(output, 5); failures.extend(sf)
        coverage = [set(pred) == {row["material_id"] for row in ORACLE["rows"]}, len(rows) == len(ORACLE["rows"]), not schema_failures]
        criteria = [exact("结构解析", 30, sum(parse_checks), len(parse_checks)), exact("一致性误差", 20, sum(error_checks), len(error_checks)), exact("CIF 质检", 15, sum(cif_checks), len(cif_checks)), exact("覆盖与格式", 5, sum(coverage), len(coverage)), script, report_criterion(output)]
        if not all(coverage): failures.append("HG_ID_COVERAGE")
        metrics.update({"structure_parse_accuracy": sum(parse_checks) / len(parse_checks)})

    elif qid == "MS05-Q3":
        pred = {(str(row.get("sentence_id", "")), str(row.get("token_id", ""))): row for row in rows}
        gold_rows = ORACLE["test_labels"]
        keys = [(str(row["sentence_id"]), str(row["token_id"])) for row in gold_rows]
        gt = [row["token_label"] for row in gold_rows]; pt = [pred.get(key, {}).get("token_label", "__MISSING__") for key in keys]
        gs = [row["slot_label"] for row in gold_rows]; ps = [pred.get(key, {}).get("slot_label", "__MISSING__") for key in keys]
        token_f1 = macro_f1(gt, pt); slot_f1 = macro_f1(gs, ps)
        gold_entities = extract_bio_entities(gold_rows, "slot_label"); pred_entities = extract_bio_entities(rows, "slot_label")
        entity_f1, tp, npred, ngold = set_f1(pred_entities, gold_entities)
        coverage = sum(key in pred for key in keys)
        criteria = [criterion("token label F1", 25, token_f1), criterion("slot label F1", 30, slot_f1), criterion("实体 span F1", 10, entity_f1, f"TP={tp}, pred={npred}, gold={ngold}"), exact("覆盖与对齐", 10, coverage, len(keys)), report_criterion(output)]
        if coverage != len(keys) or len(pred) != len(keys): failures.append("HG_TOKEN_ALIGNMENT")
        metrics.update({"token_macro_f1": token_f1, "slot_macro_f1": slot_f1, "entity_f1": entity_f1})

    elif qid in {"MS06-Q1", "MS08-Q1", "MS09-Q1", "MS09-Q3"}:
        config = REGRESSION_CONFIG[qid]
        pred = {str(row.get(config["id_key"], "")): row for row in rows}
        gold_rows = ORACLE["test_labels"]
        ids = [str(row[config["id_key"]]) for row in gold_rows]
        gold = [float(row[config["gold_col"]]) for row in gold_rows]
        values: list[float] = []
        valid = 0
        for sid in ids:
            value = pred.get(sid, {}).get(config["pred_col"])
            if finite(value) and float(value) >= 0:
                values.append(float(value)); valid += 1
            else:
                values.append(float("nan"))
        if valid == len(ids):
            train_rows = read_csv(workspace / "inputs" / "train.csv")[1]
            baseline = statistics.median(float(row[config["train_col"]]) for row in train_rows)
            reg = regression_metrics(gold, values, baseline)
        else:
            reg = {"mae": float("inf"), "rmse": float("inf"), "baseline_mae": 0.0, "mae_improvement": 0.0, "r2": float("-inf"), "r2_clipped": 0.0}
        criteria = [criterion(config["mae_name"], config["mae_weight"], reg["mae_improvement"], f"MAE={reg['mae']}, baseline_MAE={reg['baseline_mae']}")]
        if config["r2_weight"]:
            criteria.append(criterion("隐藏测试 R²", config["r2_weight"], reg["r2_clipped"], f"R2={reg['r2']}"))
        criteria.append(exact(config["coverage_name"], config["coverage_weight"], valid, len(ids)))
        if qid == "MS09-Q3":
            protocol = read_json(output / "ood_protocol.json")
            checks = [str(protocol.get("preprocessing_fit_scope", protocol.get("preprocessing_fit", ""))).replace("_", " ").casefold() == "train only", str(protocol.get("model_fit_scope", "train only" if protocol.get("test_used_for_tuning") is False else "")).replace("_", " ").casefold() == "train only", protocol.get("ood_test_used_for_tuning", protocol.get("test_used_for_tuning")) is False, int(protocol.get("train_rows", -1)) == 700, int(protocol.get("ood_test_rows", protocol.get("ood_rows", -1))) == 180]
            criteria.append(exact("OOD 协议", 15, sum(checks), len(checks)))
            cv_weight = 10
        else:
            cv_weight = config["protocol_weight"]
        cv = read_json(output / "cv_metrics.json") if (output / "cv_metrics.json").is_file() else {}
        cv_checks = [int(cv.get("n_splits", 0)) == 5, cv.get("seed") is not None, "fold" in str(cv.get("splitter", "")).casefold()]
        criteria.append(exact("训练 CV" if qid == "MS09-Q3" else "验证协议", cv_weight, sum(cv_checks), len(cv_checks)))
        if config["plot_weight"]:
            criteria.append(plot_criterion(output, "parity.png", config["plot_weight"]))
        if config["repro_weight"]:
            script, sf = script_criterion(output, config["repro_weight"]); criteria.append(script); failures.extend(sf)
        criteria.append(report_criterion(output))
        if valid != len(ids) or len(pred) != len(ids): failures.append("HG_ID_OR_NUMERIC_RANGE")
        metrics.update(reg)

    elif qid == "MS06-Q2":
        pred = {str(row.get("sample_id", "")): row for row in rows}
        numeric: list[bool] = []; classes: list[bool] = []
        for gold in ORACLE["rows"]:
            row = pred.get(str(gold["sample_id"]), {})
            numeric.extend([finite(row.get("k_gpa")) and abs(float(row["k_gpa"]) - gold["k_gpa"]) <= 1e-6 * max(abs(gold["k_gpa"]), 1), finite(row.get("g_gpa")) and abs(float(row["g_gpa"]) - gold["g_gpa"]) <= 1e-6 * max(abs(gold["g_gpa"]), 1), finite(row.get("pugh_k_over_g")) and abs(float(row["pugh_k_over_g"]) - gold["pugh_k_over_g"]) <= 1e-6 * max(abs(gold["pugh_k_over_g"]), 1)])
            classes.append(row.get("class") == gold["class"])
        expected = [str(row["sample_id"]) for row in sorted(ORACLE["rows"], key=lambda row: (-row["pugh_k_over_g"], str(row["sample_id"])))]
        actual = [row["sample_id"] for row in sorted(rows, key=lambda row: int(float(row["rank"]))) if row.get("rank")]
        rank = sum(a == b for a, b in zip(actual, expected))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("K/G 数值", 40, sum(numeric), len(numeric)), exact("类别", 15, sum(classes), len(classes)), exact("排名", 10, rank, len(expected)), script, report_criterion(output)]
        if set(pred) != {str(row["sample_id"]) for row in ORACLE["rows"]}: failures.append("HG_ID_COVERAGE")
        metrics.update({"numeric_accuracy": sum(numeric) / len(numeric), "class_accuracy": sum(classes) / len(classes)})

    elif qid == "MS06-Q3":
        pred = {row.get("jid", ""): row for row in rows}
        status: list[bool] = []; ratio: list[bool] = []; classes: list[bool] = []
        for gold in ORACLE["rows"]:
            row = pred.get(gold["jid"], {})
            valid = gold["status"] == "ok"
            status.append((row.get("status") == "valid") if valid else row.get("status") == gold["status"])
            if valid:
                ratio.append(finite(row.get("pugh_k_over_g")) and abs(float(row["pugh_k_over_g"]) - gold["pugh_k_over_g"]) <= 1e-8 * max(abs(gold["pugh_k_over_g"]), 1))
                classes.append(row.get("proxy_class") == ("ductile_proxy" if gold["pugh_k_over_g"] >= 1.75 else "brittle_proxy"))
        valid_gold = [row for row in ORACLE["rows"] if row["status"] == "ok"]
        expected = [row["jid"] for row in sorted(valid_gold, key=lambda row: (-row["pugh_k_over_g"], row["jid"]))]
        actual = [row["jid"] for row in sorted((row for row in rows if row.get("rank")), key=lambda row: int(float(row["rank"])))]
        rank = sum(a == b for a, b in zip(actual, expected))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("物理有效性", 25, sum(status), len(status)), exact("K/G 与类别", 30, sum(ratio) + sum(classes), len(ratio) + len(classes)), exact("稳定排名", 10, rank, len(expected)), script, report_criterion(output)]
        if not all(status): failures.append("HG_PHYSICS_GATE")
        metrics.update({"status_accuracy": sum(status) / len(status), "valid_rank_accuracy": rank / len(expected)})

    elif qid == "MS08-Q2":
        pred = {row.get("material_id", ""): row for row in rows}
        gold_rows = ORACLE["test_labels"]
        ids = [row["material_id"] for row in gold_rows]
        gold = [float(row["band_gap"]) for row in gold_rows]
        a = [float(pred[sid]["pred_formula_only_ev"]) for sid in ids]
        b = [float(pred[sid]["pred_formula_description_ev"]) for sid in ids]
        train = read_csv(workspace / "inputs" / "train.csv")[1]
        baseline = statistics.median(float(row["band_gap"]) for row in train)
        ma = regression_metrics(gold, a, baseline); mb = regression_metrics(gold, b, baseline)
        summary = read_json(output / "summary.json")
        stated = summary.get("mean_abs_A_B_difference")
        actual_diff = sum(abs(x - y) for x, y in zip(a, b)) / len(a)
        checks = [set(pred) == set(ids), len(rows) == len(ids), all(finite(value) and value >= 0 for value in a + b), stated is not None and abs(float(stated) - actual_diff) <= 1e-12]
        cv = read_json(output / "cv_metrics.json")
        protocol = [cv.get("same_folds", cv.get("same_split")) is True, cv.get("seed") is not None, cv.get("model_b_oof_mae") is not None]
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [criterion("B 模型隐藏 MAE", 25, mb["mae_improvement"]), criterion("A 模型隐藏 MAE", 15, ma["mae_improvement"]), exact("A/B 差异与覆盖", 10, sum(checks), len(checks)), exact("消融协议", 15, sum(protocol), len(protocol)), script, report_criterion(output)]
        if not all(checks[:3]): failures.append("HG_PAIRED_ID_OR_RANGE")
        metrics.update({"mae_a": ma["mae"], "mae_b": mb["mae"], "delta_mae_b_minus_a": mb["mae"] - ma["mae"]})

    elif qid == "MS08-Q3":
        pred = {row.get("jid", ""): row for row in rows}
        fields = ["n_points", "peak_point_id", "peak_value", "mean", "std", "auc"]
        checks: list[bool] = []
        for gold in DERIVED_GOLD["rows"]:
            row = pred.get(gold["jid"], {})
            for field in fields:
                if field in {"n_points", "peak_point_id"}:
                    checks.append(str(int(float(row.get(field, -1)))) == str(int(gold[field])))
                else:
                    checks.append(finite(row.get(field)) and abs(float(row[field]) - float(gold[field])) <= 1e-8)
        expected = [row["jid"] for row in sorted(DERIVED_GOLD["rows"], key=lambda row: (-row["peak_value"], row["jid"]))]
        actual = [row["jid"] for row in sorted(rows, key=lambda row: int(float(row["rank"]))) if row.get("rank")]
        rank = sum(a == b for a, b in zip(actual, expected))
        script, sf = script_criterion(output, 10); failures.extend(sf)
        criteria = [exact("谱统计", 40, sum(checks), len(checks)), exact("峰值与排名", 15, rank, len(expected)), plot_criterion(output, "dielectric_spectra.png", 10), script, report_criterion(output)]
        if set(pred) != set(expected): failures.append("HG_SPECTRUM_COVERAGE")
        metrics.update({"spectral_field_accuracy": sum(checks) / len(checks), "rank_accuracy": rank / len(expected)})

    elif qid == "MS09-Q2":
        pred = {row.get("jid", ""): row for row in rows}
        gold = ORACLE["valid_ranked"]
        audit = sum(gold_row["jid"] in pred and pred[gold_row["jid"]].get("status") == "valid" and finite(pred[gold_row["jid"]].get("heat_capacity")) and abs(float(pred[gold_row["jid"]]["heat_capacity"]) - gold_row["heat_capacity"]) <= 1e-10 for gold_row in gold)
        expected = [row["jid"] for row in gold]
        actual = [row["jid"] for row in sorted(rows, key=lambda row: int(float(row["rank"]))) if row.get("rank")]
        rank = sum(a == b for a, b in zip(actual, expected))
        summary = read_json(output / "summary.json")
        quantile_checks = 0
        for key, value in DERIVED_GOLD["quantiles"].items():
            actual_value = summary.get("quantiles", {}).get(key)
            quantile_checks += actual_value is not None and abs(float(actual_value) - value) <= 1e-10
        script, sf = script_criterion(output, 5); failures.extend(sf)
        criteria = [exact("物理审计", 25, audit, len(gold)), exact("排名", 30, rank, len(expected)), exact("统计汇总", 15, quantile_checks, len(DERIVED_GOLD["quantiles"])), script, report_criterion(output)]
        if audit != len(gold): failures.append("HG_INVALID_INCLUDED_OR_VALUE_CHANGED")
        metrics.update({"valid_value_accuracy": audit / len(gold), "rank_accuracy": rank / len(expected)})

    elif qid.startswith("MS10-"):
        audit = read_json(output / "safety_audit.json")
        predicted_flags = {flag.get("code", ""): flag for flag in audit.get("flags", [])}
        gold_flags = {flag["code"]: flag for flag in ORACLE["flags"]}
        code_tp = len(set(predicted_flags) & set(gold_flags))
        code_f1, _, _, _ = set_f1(set(predicted_flags), set(gold_flags))
        procedure = (workspace / "inputs" / "procedure.txt").read_text(encoding="utf-8")
        evidence_total = 0; evidence_ok = 0
        all_evidence: list[str] = []
        for flag in audit.get("flags", []):
            all_evidence.extend(flatten_strings(flag))
        for code, gold_flag in gold_flags.items():
            predicted_text = " ".join(flatten_strings(predicted_flags.get(code, {})))
            for hit in gold_flag["hits"]:
                evidence_total += 1
                positions = [match.start() for match in re.finditer(re.escape(str(hit)), procedure, re.I)]
                text_match = norm(hit) in norm(predicted_text)
                offset_values = [int(value) for value in re.findall(r"\b\d+\b", predicted_text)]
                offset_match = not positions or any(position in offset_values for position in positions)
                evidence_ok += text_match and offset_match
        severity_ok = audit.get("severity") == ORACLE["severity"]
        anchor_ok = sum(any(norm(hit) in norm(text) for text in all_evidence) for flag in ORACLE["flags"] for hit in flag["hits"])
        anchor_total = sum(len(flag["hits"]) for flag in ORACLE["flags"])
        criteria = [criterion("规则触发", 35, code_f1, f"TP={code_tp}, pred={len(predicted_flags)}, gold={len(gold_flags)}"), exact("证据 offset", 20, evidence_ok, evidence_total), exact("severity", 10, int(severity_ok), 1), exact("实体与条件覆盖", 10, anchor_ok, anchor_total), report_criterion(output)]
        if set(predicted_flags) != set(gold_flags) or evidence_ok != evidence_total or not severity_ok: failures.append("HG_SAFETY_RULE_EVIDENCE")
        metrics.update({"flag_f1": code_f1, "evidence_accuracy": evidence_ok / evidence_total if evidence_total else 1.0, "severity_exact": severity_ok})

    else:
        raise KeyError(f"No scorer for {qid}")

    if abs(sum(item["max_points"] for item in criteria) - 80.0) > 1e-9:
        raise ValueError(f"criteria max does not sum to 80: {sum(item['max_points'] for item in criteria)}")
    return criteria, failures, metrics


def zero_criteria() -> list[dict[str, Any]]:
    return [criterion(name, maximum, 0.0, "not scoreable") for name, maximum in CRITERIA_LAYOUT]


def grade(workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    output = workspace / "output"
    input_ok, input_failures = verify_inputs(workspace)
    if not input_ok:
        return {
            "task_id": TASK_ID,
            "grader_version": GRADER_VERSION,
            "grader_status": "invalid",
            "hardgate_pass": False,
            "deterministic_score": 0.0,
            "max_score": 80.0,
            "criteria": zero_criteria(),
            "failure_codes": sorted(input_failures),
            "metrics": {},
            "oracle_sha256": EMBEDDED_ORACLE_SHA256,
            "scoring_spec": SCORING_SPEC,
        }

    deliverables_ok, failures = required_artifacts(output)
    try:
        criteria, science_failures, metrics = score_task(workspace)
        failures.extend(science_failures)
    except Exception as exc:
        criteria = zero_criteria()
        metrics = {}
        failures.append(f"HG_GRADER_EXCEPTION:{type(exc).__name__}:{exc}")

    if not deliverables_ok:
        failures.append("HG_DELIVERABLE_SET")
    failures = list(dict.fromkeys(failures))
    hardgate_failures = [code for code in failures if code.startswith("HG_")]
    score = sum(float(item["points"]) for item in criteria)
    return {
        "task_id": TASK_ID,
        "grader_version": GRADER_VERSION,
        "grader_status": "scored",
        "hardgate_pass": not hardgate_failures,
        "deterministic_score": score,
        "max_score": 80.0,
        "criteria": criteria,
        "failure_codes": sorted(failures),
        "metrics": metrics,
        "oracle_sha256": EMBEDDED_ORACLE_SHA256,
        "scoring_spec": SCORING_SPEC,
    }


def json_safe(value: Any) -> Any:
    """Replace diagnostic non-finite floats with JSON null."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: json_safe(child) for key, child in value.items()}
    if isinstance(value, list):
        return [json_safe(child) for child in value]
    if isinstance(value, tuple):
        return [json_safe(child) for child in value]
    return value


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True, help="Task workspace containing inputs/ and output/")
    parser.add_argument("--json-out", type=Path, help="Optional path for the JSON result")
    args = parser.parse_args()
    result = json_safe(grade(args.workspace))
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    if result["grader_status"] == "invalid":
        return 2
    return 0 if result["hardgate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
