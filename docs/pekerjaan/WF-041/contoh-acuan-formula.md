# Contoh acuan independen

Versi 1 · 23 Oktober 2026 · Penyusun: Codex. Semua baris sintetis, tidak bagian penelitian. Expected dihitung dari matematika/Decimal, bukan memanggil modul implementasi yang belum ada.

| P | F | A | T | density | ratio | need | deficit | without_facility |
|---:|---:|---:|---:|---|---|---:|---:|---|
| 30000 | 1 | 2 | 30000 | 15000 | 30000 | 1 | 0 | false |
| 30001 | 1 | 2 | 30000 | 15000.5 | 30001 | 2 | 1 | false |
| 60000 | 2 | 10 | 30000 | 6000 | 30000 | 2 | 0 | false |
| 10000 | 0 | 2 | 30000 | 5000 | null | 1 | 1 | true |
| 0 | 0 | 2 | 30000 | 0 | null | 0 | 0 | true |
| null | 1 | 2 | 30000 | null | null | null | null | false |
| 60000 | 3 | null | 30000 | null | 20000 | 2 | 0 | false |
| 90001 | 1 | 2 | 30000 | 45000.5 | 90001 | 4 | 3 | false |
| 60000 | 2 | 10 | 20000 | 6000 | 30000 | 3 | 1 | false |

A0/negative rejected input, not valid density0. P negative/F negative/T0 rejected. Aggregate(30000/1,90000/2)=120000/3=40000, not (30000+45000)/2=37500. Districts30001/F1 and29999/F1: individual deficits1+0=1, although aggregate recomputation yields0; expected sum stays1. Missing P in one member makes full aggregate null, labeled complete subset retains own F only.

Rounding sample Decimal1.005→display1.01 HALF_UP; internal remains1.005. Coordinate quality565/973×100≈58.0678314491%, display58.07%, but verified percentage cannot be inferred. Machine-readable formula fixtures and independent checker will be included with WF-049/052; document table is acceptance oracle, not production function output.
