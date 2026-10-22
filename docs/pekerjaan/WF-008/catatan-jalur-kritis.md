# Dependensi dan jalur kritis

Versi 1 — 23 Oktober 2026. Katalog 160 tiket adalah sumber dependensi. Dengan kebijakan finish-to-start utama, seluruh tiket scope terpilih membentuk rantai kritis urutan. Dependensi hasil menambah syarat masuk dan tidak memberikan izin melewati predecessor. Gerbang, review dan push menambah waktu tunggu yang belum terukur.

Tabel berikut adalah earliest start/finish dalam **jam usaha dasar serial**, tanpa cadangan/waktu tunggu. Ini koordinat usaha, bukan jam kalender. ES tiket pertama=0; EF=ES+pelaksanaan+review+perbaikan; ES berikut=EF sebelumnya. Untuk P0-only, hapus usaha WF-097–100 hanya setelah deferred resmi lalu sisipkan 1 jam keputusan. Kalender tetap menunggu kapasitas PIC.

| Tiket | Predecessor | Dependensi hasil | ES | EF |
|---|---|---|---:|---:|
| WF-001 | - | - | 0.00 | 5.60 |
| WF-002 | WF-001 | WF-001:done | 5.60 | 8.40 |
| WF-003 | WF-002 | WF-001:done, WF-002:done | 8.40 | 12.60 |
| WF-004 | WF-003 | WF-001:done, WF-002:done, WF-003:done | 12.60 | 18.20 |
| WF-005 | WF-004 | WF-004:done | 18.20 | 22.40 |
| WF-006 | WF-005 | WF-002:done, WF-005:done | 22.40 | 26.60 |
| WF-007 | WF-006 | WF-004:done, WF-006:done | 26.60 | 30.80 |
| WF-008 | WF-007 | WF-005:done, WF-006:done, WF-007:done | 30.80 | 37.80 |
| WF-009 | WF-008 | WF-005:done, WF-008:done, WF-007:done | 37.80 | 42.00 |
| WF-010 | WF-009 | WF-002:done, WF-005:done, WF-009:done | 42.00 | 46.20 |
| WF-011 | WF-010 | WF-005:done, WF-006:done, WF-010:done | 46.20 | 50.40 |
| WF-012 | WF-011 | WF-004:done, WF-005:done, WF-006:done, WF-008:done, WF-007:done, WF-009:done, WF-010:done, WF-011:done, WF-001:done, WF-002:done, WF-003:done | 50.40 | 54.60 |
| WF-013 | WF-012 | WF-012:done | 54.60 | 60.20 |
| WF-014 | WF-013 | WF-013:done, WF-005:done | 60.20 | 67.20 |
| WF-015 | WF-014 | WF-013:done, WF-014:done | 67.20 | 71.40 |
| WF-016 | WF-015 | WF-013:done, WF-014:done, WF-015:done | 71.40 | 77.00 |
| WF-017 | WF-016 | WF-001:done, WF-014:done | 77.00 | 85.40 |
| WF-018 | WF-017 | WF-017:done | 85.40 | 96.60 |
| WF-019 | WF-018 | WF-017:done, WF-018:done | 96.60 | 102.20 |
| WF-020 | WF-019 | WF-019:done | 102.20 | 109.20 |
| WF-021 | WF-020 | WF-019:done, WF-020:done | 109.20 | 116.20 |
| WF-022 | WF-021 | WF-016:done, WF-021:done | 116.20 | 121.80 |
| WF-023 | WF-022 | WF-020:done, WF-021:done | 121.80 | 128.80 |
| WF-024 | WF-023 | WF-021:done, WF-022:done, WF-023:done | 128.80 | 133.00 |
| WF-025 | WF-024 | WF-016:done, WF-022:done | 133.00 | 137.20 |
| WF-026 | WF-025 | WF-015:done, WF-020:done, WF-007:done | 137.20 | 142.80 |
| WF-027 | WF-026 | WF-014:done, WF-024:done, WF-025:done, WF-026:done | 142.80 | 149.80 |
| WF-028 | WF-027 | WF-013:done, WF-014:done, WF-015:done, WF-016:done, WF-017:done, WF-018:done, WF-019:done, WF-020:done, WF-021:done, WF-022:done, WF-023:done, WF-024:done, WF-025:done, WF-026:done, WF-027:done | 149.80 | 155.40 |
| WF-029 | WF-028 | WF-028:done | 155.40 | 162.40 |
| WF-030 | WF-029 | WF-029:done, WF-007:done | 162.40 | 168.00 |
| WF-031 | WF-030 | WF-029:done, WF-030:done | 168.00 | 176.40 |
| WF-032 | WF-031 | WF-029:done, WF-020:done | 176.40 | 183.40 |
| WF-033 | WF-032 | WF-029:done, WF-019:done, WF-021:done | 183.40 | 194.60 |
| WF-034 | WF-033 | WF-033:done | 194.60 | 203.00 |
| WF-035 | WF-034 | WF-033:done, WF-015:done, WF-026:done | 203.00 | 210.00 |
| WF-036 | WF-035 | WF-033:done, WF-035:done, WF-026:done | 210.00 | 221.20 |
| WF-037 | WF-036 | WF-032:done, WF-018:done, WF-019:done | 221.20 | 232.40 |
| WF-038 | WF-037 | WF-037:done, WF-020:done, WF-033:done | 232.40 | 243.60 |
| WF-039 | WF-038 | WF-037:done, WF-020:done, WF-033:done | 243.60 | 252.00 |
| WF-040 | WF-039 | WF-037:done, WF-038:done, WF-039:done, WF-034:done | 252.00 | 260.40 |
| WF-041 | WF-040 | WF-021:done, WF-033:done | 260.40 | 268.80 |
| WF-042 | WF-041 | WF-023:done, WF-039:done | 268.80 | 280.00 |
| WF-043 | WF-042 | WF-022:done, WF-041:done, WF-042:done | 280.00 | 287.00 |
| WF-044 | WF-043 | WF-041:done, WF-042:done, WF-043:done, WF-024:done | 287.00 | 294.00 |
| WF-045 | WF-044 | WF-033:done, WF-035:done, WF-043:done | 294.00 | 301.00 |
| WF-046 | WF-045 | WF-016:done, WF-045:done | 301.00 | 308.00 |
| WF-047 | WF-046 | WF-045:done, WF-046:done | 308.00 | 315.00 |
| WF-048 | WF-047 | WF-014:done, WF-015:done, WF-046:done, WF-036:done | 315.00 | 320.60 |
| WF-049 | WF-048 | WF-040:done, WF-041:done, WF-042:done, WF-035:done | 320.60 | 331.80 |
| WF-050 | WF-049 | WF-049:done, WF-045:done, WF-025:done, WF-026:done | 331.80 | 340.20 |
| WF-051 | WF-050 | WF-027:done, WF-046:done, WF-050:done | 340.20 | 347.20 |
| WF-052 | WF-051 | WF-029:done, WF-030:done, WF-031:done, WF-032:done, WF-033:done, WF-034:done, WF-035:done, WF-036:done, WF-037:done, WF-038:done, WF-039:done, WF-040:done, WF-041:done, WF-042:done, WF-043:done, WF-044:done, WF-045:done, WF-046:done, WF-047:done, WF-048:done, WF-049:done, WF-050:done, WF-051:done | 347.20 | 355.60 |
| WF-053 | WF-052 | WF-052:done, WF-031:done | 355.60 | 359.80 |
| WF-054 | WF-053 | WF-053:done, WF-030:done | 359.80 | 366.80 |
| WF-055 | WF-054 | WF-053:done, WF-030:done, WF-049:done | 366.80 | 373.80 |
| WF-056 | WF-055 | WF-054:done, WF-055:done, WF-031:done | 373.80 | 385.00 |
| WF-057 | WF-056 | WF-055:done, WF-037:done | 385.00 | 401.80 |
| WF-058 | WF-057 | WF-055:done, WF-037:done, WF-057:done | 401.80 | 424.20 |
| WF-059 | WF-058 | WF-055:done, WF-037:done, WF-019:done | 424.20 | 441.00 |
| WF-060 | WF-059 | WF-057:done, WF-058:done, WF-059:done, WF-032:done | 441.00 | 452.20 |
| WF-061 | WF-060 | WF-060:done | 452.20 | 460.60 |
| WF-062 | WF-061 | WF-061:done, WF-038:done, WF-040:done | 460.60 | 483.00 |
| WF-063 | WF-062 | WF-062:done, WF-059:done, WF-038:done | 483.00 | 511.00 |
| WF-064 | WF-063 | WF-062:done, WF-063:done | 511.00 | 525.00 |
| WF-065 | WF-064 | WF-062:done, WF-063:done, WF-019:done | 525.00 | 541.80 |
| WF-066 | WF-065 | WF-059:done, WF-063:done, WF-042:done | 541.80 | 558.60 |
| WF-067 | WF-066 | WF-064:done, WF-066:done, WF-039:done | 558.60 | 567.00 |
| WF-068 | WF-067 | WF-067:done | 567.00 | 632.91 |
| WF-069 | WF-068 | WF-067:done, WF-068:done | 632.91 | 747.15 |
| WF-070 | WF-069 | WF-068:done, WF-069:done, WF-066:done | 747.15 | 769.55 |
| WF-071 | WF-070 | WF-070:done, WF-065:done, WF-066:done, WF-020:done | 769.55 | 776.55 |
| WF-072 | WF-071 | WF-054:done, WF-033:done, WF-030:done | 776.55 | 784.95 |
| WF-073 | WF-072 | WF-072:done, WF-034:done | 784.95 | 804.55 |
| WF-074 | WF-073 | WF-073:done, WF-035:done, WF-036:done | 804.55 | 818.55 |
| WF-075 | WF-074 | WF-074:done, WF-040:done | 818.55 | 840.95 |
| WF-076 | WF-075 | WF-075:done, WF-071:done, WF-064:done, WF-065:done, WF-066:done | 840.95 | 849.35 |
| WF-077 | WF-076 | WF-076:done, WF-041:done | 849.35 | 863.35 |
| WF-078 | WF-077 | WF-077:done | 863.35 | 874.55 |
| WF-079 | WF-078 | WF-077:done, WF-071:done, WF-042:done | 874.55 | 888.55 |
| WF-080 | WF-079 | WF-079:done, WF-066:done | 888.55 | 908.15 |
| WF-081 | WF-080 | WF-078:done, WF-080:done, WF-043:done | 908.15 | 919.35 |
| WF-082 | WF-081 | WF-076:done, WF-074:done, WF-045:done | 919.35 | 930.55 |
| WF-083 | WF-082 | WF-082:done, WF-045:done | 930.55 | 944.55 |
| WF-084 | WF-083 | WF-082:done, WF-081:done, WF-045:done | 944.55 | 961.35 |
| WF-085 | WF-084 | WF-054:done, WF-074:done, WF-035:done | 961.35 | 975.35 |
| WF-086 | WF-085 | WF-085:done, WF-075:done, WF-081:done, WF-036:done | 975.35 | 1008.95 |
| WF-087 | WF-086 | WF-082:done, WF-084:done, WF-046:done | 1008.95 | 1020.15 |
| WF-088 | WF-087 | WF-087:done, WF-084:done | 1020.15 | 1034.15 |
| WF-089 | WF-088 | WF-088:done, WF-083:done, WF-047:done | 1034.15 | 1045.35 |
| WF-090 | WF-089 | WF-089:done, WF-081:done, WF-084:done | 1045.35 | 1062.15 |
| WF-091 | WF-090 | WF-089:done, WF-083:done, WF-084:done | 1062.15 | 1076.15 |
| WF-092 | WF-091 | WF-087:done, WF-088:done, WF-089:done, WF-090:done, WF-091:done, WF-047:done | 1076.15 | 1084.55 |
| WF-093 | WF-092 | WF-081:done, WF-044:done, WF-055:done | 1084.55 | 1092.95 |
| WF-094 | WF-093 | WF-093:done, WF-077:done, WF-078:done, WF-079:done, WF-080:done | 1092.95 | 1106.95 |
| WF-095 | WF-094 | WF-094:done, WF-043:done | 1106.95 | 1118.15 |
| WF-096 | WF-095 | WF-095:done, WF-044:done | 1118.15 | 1126.55 |
| WF-097 | WF-096 | WF-028:done, WF-085:done, WF-086:done, WF-048:done | 1126.55 | 1143.35 |
| WF-098 | WF-097 | WF-028:done, WF-097:done_or_approved_deferred, WF-086:done, WF-048:done | 1143.35 | 1165.75 |
| WF-099 | WF-098 | WF-028:done, WF-083:done, WF-091:done | 1165.75 | 1174.15 |
| WF-100 | WF-099 | WF-028:done, WF-077:done, WF-078:done, WF-091:done | 1174.15 | 1188.15 |
| WF-101 | WF-100 | WF-076:done, WF-081:done, WF-086:done, WF-092:done, WF-096:done, WF-097:done_or_approved_deferred, WF-098:done_or_approved_deferred, WF-099:done_or_approved_deferred, WF-100:done_or_approved_deferred | 1188.15 | 1210.55 |
| WF-102 | WF-101 | WF-101:done, WF-049:done | 1210.55 | 1238.55 |
| WF-103 | WF-102 | WF-102:done | 1238.55 | 1260.95 |
| WF-104 | WF-103 | WF-101:done, WF-102:done, WF-103:done, WF-071:done, WF-053:done, WF-054:done, WF-055:done, WF-056:done, WF-057:done, WF-058:done, WF-059:done, WF-060:done, WF-061:done, WF-062:done, WF-063:done, WF-064:done, WF-065:done, WF-066:done, WF-067:done, WF-068:done, WF-069:done, WF-070:done, WF-072:done, WF-073:done, WF-074:done, WF-075:done, WF-076:done, WF-077:done, WF-078:done, WF-079:done, WF-080:done, WF-081:done, WF-082:done, WF-083:done, WF-084:done, WF-085:done, WF-086:done, WF-087:done, WF-088:done, WF-089:done, WF-090:done, WF-091:done, WF-092:done, WF-093:done, WF-094:done, WF-095:done, WF-096:done, WF-097:done_or_approved_deferred, WF-098:done_or_approved_deferred, WF-099:done_or_approved_deferred, WF-100:done_or_approved_deferred | 1260.95 | 1269.35 |
| WF-105 | WF-104 | WF-104:done, WF-050:done | 1269.35 | 1277.75 |
| WF-106 | WF-105 | WF-104:done, WF-064:done, WF-076:done | 1277.75 | 1286.15 |
| WF-107 | WF-106 | WF-104:done, WF-063:done, WF-065:done, WF-066:done | 1286.15 | 1297.35 |
| WF-108 | WF-107 | WF-105:done, WF-106:done, WF-107:done | 1297.35 | 1305.75 |
| WF-109 | WF-108 | WF-104:done, WF-041:done, WF-077:done, WF-078:done | 1305.75 | 1316.95 |
| WF-110 | WF-109 | WF-104:done, WF-071:done, WF-081:done | 1316.95 | 1328.15 |
| WF-111 | WF-110 | WF-110:done, WF-079:done, WF-080:done, WF-042:done | 1328.15 | 1344.95 |
| WF-112 | WF-111 | WF-111:done, WF-042:done | 1344.95 | 1358.95 |
| WF-113 | WF-112 | WF-104:done, WF-073:done, WF-075:done | 1358.95 | 1367.35 |
| WF-114 | WF-113 | WF-113:done, WF-086:done, WF-084:done | 1367.35 | 1381.35 |
| WF-115 | WF-114 | WF-114:done, WF-085:done, WF-088:done | 1381.35 | 1395.35 |
| WF-116 | WF-115 | WF-115:done, WF-074:done, WF-095:done | 1395.35 | 1406.55 |
| WF-117 | WF-116 | WF-104:done, WF-089:done, WF-091:done | 1406.55 | 1414.95 |
| WF-118 | WF-117 | WF-117:done, WF-090:done, WF-092:done | 1414.95 | 1423.35 |
| WF-119 | WF-118 | WF-118:done, WF-047:done, WF-025:done | 1423.35 | 1434.55 |
| WF-120 | WF-119 | WF-119:done, WF-097:done_or_approved_deferred, WF-098:done_or_approved_deferred, WF-099:done_or_approved_deferred, WF-100:done_or_approved_deferred, WF-075:done | 1434.55 | 1445.75 |
| WF-121 | WF-120 | WF-119:done, WF-116:done, WF-025:done | 1445.75 | 1456.95 |
| WF-122 | WF-121 | WF-116:done, WF-036:done, WF-026:done | 1456.95 | 1468.15 |
| WF-123 | WF-122 | WF-112:done, WF-096:done | 1468.15 | 1479.35 |
| WF-124 | WF-123 | WF-123:done, WF-092:done | 1479.35 | 1486.35 |
| WF-125 | WF-124 | WF-108:done, WF-112:done, WF-116:done, WF-120:done, WF-121:done, WF-122:done, WF-124:done, WF-051:done | 1486.35 | 1491.95 |
| WF-126 | WF-125 | WF-125:done | 1491.95 | 1503.15 |
| WF-127 | WF-126 | WF-126:done | 1503.15 | 1525.55 |
| WF-128 | WF-127 | WF-108:done, WF-112:done, WF-116:done, WF-120:done, WF-121:done, WF-122:done, WF-124:done, WF-127:done, WF-105:done, WF-106:done, WF-107:done, WF-109:done, WF-110:done, WF-111:done, WF-113:done, WF-114:done, WF-115:done, WF-117:done, WF-118:done, WF-119:done, WF-123:done, WF-125:done, WF-126:done | 1525.55 | 1533.95 |
| WF-129 | WF-128 | WF-128:done, WF-030:done, WF-007:done | 1533.95 | 1542.35 |
| WF-130 | WF-129 | WF-129:done, WF-035:done, WF-036:done | 1542.35 | 1549.35 |
| WF-131 | WF-130 | WF-129:done, WF-130:done, WF-122:done, WF-128:done | 1549.35 | 1556.35 |
| WF-132 | WF-131 | WF-131:done, WF-128:done | 1556.35 | 1561.95 |
| WF-133 | WF-132 | WF-132:done, WF-130:done, WF-131:done, WF-076:done | 1561.95 | 1567.55 |
| WF-134 | WF-133 | WF-133:done, WF-129:done, WF-130:done, WF-085:done | 1567.55 | 1573.15 |
| WF-135 | WF-134 | WF-133:done, WF-134:done, WF-132:done, WF-128:done | 1573.15 | 1578.75 |
| WF-136 | WF-135 | WF-135:done, WF-134:done, WF-036:done | 1578.75 | 1587.15 |
| WF-137 | WF-136 | WF-136:done | 1587.15 | 1592.75 |
| WF-138 | WF-137 | WF-137:done, WF-136:done, WF-134:done | 1592.75 | 1598.35 |
| WF-139 | WF-138 | WF-137:done, WF-138:done, WF-131:done | 1598.35 | 1606.75 |
| WF-140 | WF-139 | WF-137:done, WF-138:done, WF-139:done, WF-129:done, WF-130:done, WF-131:done, WF-132:done, WF-133:done, WF-134:done, WF-135:done, WF-136:done | 1606.75 | 1610.95 |
| WF-141 | WF-140 | WF-140:done, WF-092:done, WF-086:done | 1610.95 | 1619.35 |
| WF-142 | WF-141 | WF-140:done, WF-131:done, WF-122:done | 1619.35 | 1630.55 |
| WF-143 | WF-142 | WF-140:done, WF-052:done, WF-101:done | 1630.55 | 1641.75 |
| WF-144 | WF-143 | WF-140:done, WF-096:done, WF-123:done, WF-124:done | 1641.75 | 1652.95 |
| WF-145 | WF-144 | WF-144:done, WF-081:done, WF-112:done | 1652.95 | 1675.35 |
| WF-146 | WF-145 | WF-143:done, WF-128:done, WF-145:done | 1675.35 | 1692.15 |
| WF-147 | WF-146 | WF-141:done, WF-145:done, WF-146:done | 1692.15 | 1703.35 |
| WF-148 | WF-147 | WF-141:done, WF-142:done, WF-143:done, WF-144:done, WF-145:done, WF-146:done, WF-147:done | 1703.35 | 1711.75 |
| WF-149 | WF-148 | WF-147:done, WF-148:done | 1711.75 | 1717.35 |
| WF-150 | WF-149 | WF-149:done, WF-142:done, WF-148:done | 1717.35 | 1722.95 |
| WF-151 | WF-150 | WF-148:done, WF-149:done, WF-150:done | 1722.95 | 1728.55 |
| WF-152 | WF-151 | WF-149:done, WF-150:done, WF-151:done, WF-141:done, WF-142:done, WF-143:done, WF-144:done, WF-145:done, WF-146:done, WF-147:done, WF-148:done | 1728.55 | 1732.75 |
| WF-153 | WF-152 | WF-152:done, WF-136:done | 1732.75 | 1741.15 |
| WF-154 | WF-153 | WF-153:per_cycle_output, WF-152:done | 1741.15 | 1746.75 |
| WF-155 | WF-154 | WF-154:per_cycle_output | 1746.75 | 1763.55 |
| WF-156 | WF-155 | WF-155:per_cycle_output | 1763.55 | 1771.95 |
| WF-157 | WF-156 | WF-153:done, WF-154:done, WF-155:done, WF-156:done, WF-008:done | 1771.95 | 1777.55 |
| WF-158 | WF-157 | WF-157:done | 1777.55 | 1783.15 |
| WF-159 | WF-158 | WF-157:done, WF-158:done, WF-150:done, WF-148:done | 1783.15 | 1788.75 |
| WF-160 | WF-159 | WF-153:done, WF-154:done, WF-155:done, WF-156:done, WF-157:done, WF-158:done, WF-159:done | 1788.75 | 1792.95 |

Bottleneck utama: kurasi 973 lokasi, crosswalk/polygon, lifecycle publish/rollback, integrasi dan retest. Pilot 25 objek mengukur ulang throughput 068/069; ketidaktersediaan polygon tidak diselesaikan dengan geometri fiktif. Cadangan 20% usaha bukan pengganti lead time sumber atau masa dukungan.
