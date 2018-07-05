from datetime import datetime

current_cache = """[
    {
        "Name": "vm 01",
        "Id": "01",
        "State": 2,
        "Uptime": {
            "Ticks": 5227649510000,
            "Days": 6,
            "Hours": 1,
            "Milliseconds": 951,
            "Minutes": 12,
            "Seconds": 44,
            "TotalDays": 6.050520266203703,
            "TotalHours": 145.2124863888889,
            "TotalMilliseconds": 522764951,
            "TotalMinutes": 8712.749183333333,
            "TotalSeconds": 522764.951
        },
        "ParentSnapshotName": null
    },
    {
        "Name": "vm 03",
        "Id": "03",
        "State": 2,
        "Uptime": {
            "Ticks": 5227649510000,
            "Days": 6,
            "Hours": 1,
            "Milliseconds": 951,
            "Minutes": 12,
            "Seconds": 44,
            "TotalDays": 6.050520266203703,
            "TotalHours": 145.2124863888889,
            "TotalMilliseconds": 522764951,
            "TotalMinutes": 8712.749183333333,
            "TotalSeconds": 522764.951
        },
        "ParentSnapshotName": null
    }
]"""

get_vm_response = """[
    {
        "Name": "vm 02",
        "Id": "02",
        "State": 2,
        "Uptime": {
            "Ticks": 5227649510000,
            "Days": 6,
            "Hours": 1,
            "Milliseconds": 951,
            "Minutes": 12,
            "Seconds": 44,
            "TotalDays": 6.050520266203703,
            "TotalHours": 145.2124863888889,
            "TotalMilliseconds": 522764951,
            "TotalMinutes": 8712.749183333333,
            "TotalSeconds": 522764.951
        },
        "ParentSnapshotName": null
    },
    {
        "Name": "vm 04",
        "Id": "04",
        "State": 2,
        "Uptime": {
            "Ticks": 5227649510000,
            "Days": 6,
            "Hours": 1,
            "Milliseconds": 951,
            "Minutes": 12,
            "Seconds": 44,
            "TotalDays": 6.050520266203703,
            "TotalHours": 145.2124863888889,
            "TotalMilliseconds": 522764951,
            "TotalMinutes": 8712.749183333333,
            "TotalSeconds": 522764.951
        },
        "ParentSnapshotName": null
    },
    {
        "Name": "vm 03-1",
        "Id": "03",
        "State": 1,
        "Uptime": {
            "Ticks": 5227649510000,
            "Days": 6,
            "Hours": 1,
            "Milliseconds": 951,
            "Minutes": 12,
            "Seconds": 44,
            "TotalDays": 6.050520266203703,
            "TotalHours": 145.2124863888889,
            "TotalMilliseconds": 522764951,
            "TotalMinutes": 8712.749183333333,
            "TotalSeconds": 522764.951
        },
        "ParentSnapshotName": null
    }
]"""

updated_cache = """[
    {
        "Name": "vm 01",
        "Id": "01",
        "State": 2,
        "Uptime": {
            "Ticks": 5227649510000,
            "Days": 6,
            "Hours": 1,
            "Milliseconds": 951,
            "Minutes": 12,
            "Seconds": 44,
            "TotalDays": 6.050520266203703,
            "TotalHours": 145.2124863888889,
            "TotalMilliseconds": 522764951,
            "TotalMinutes": 8712.749183333333,
            "TotalSeconds": 522764.951
        },
        "ParentSnapshotName": null
    },
    {
        "Name": "vm 02",
        "Id": "02",
        "State": 2,
        "Uptime": {
            "Ticks": 5227649510000,
            "Days": 6,
            "Hours": 1,
            "Milliseconds": 951,
            "Minutes": 12,
            "Seconds": 44,
            "TotalDays": 6.050520266203703,
            "TotalHours": 145.2124863888889,
            "TotalMilliseconds": 522764951,
            "TotalMinutes": 8712.749183333333,
            "TotalSeconds": 522764.951
        },
        "ParentSnapshotName": null
    },
    {
        "Name": "vm 03-1",
        "Id": "03",
        "State": 1,
        "Uptime": {
            "Ticks": 5227649510000,
            "Days": 6,
            "Hours": 1,
            "Milliseconds": 951,
            "Minutes": 12,
            "Seconds": 44,
            "TotalDays": 6.050520266203703,
            "TotalHours": 145.2124863888889,
            "TotalMilliseconds": 522764951,
            "TotalMinutes": 8712.749183333333,
            "TotalSeconds": 522764.951
        },
        "ParentSnapshotName": null
    },
    {
        "Name": "vm 04",
        "Id": "04",
        "State": 2,
        "Uptime": {
            "Ticks": 5227649510000,
            "Days": 6,
            "Hours": 1,
            "Milliseconds": 951,
            "Minutes": 12,
            "Seconds": 44,
            "TotalDays": 6.050520266203703,
            "TotalHours": 145.2124863888889,
            "TotalMilliseconds": 522764951,
            "TotalMinutes": 8712.749183333333,
            "TotalSeconds": 522764.951
        },
        "ParentSnapshotName": null
    }
]"""

snaps_json = """[
{"Name": "snap 3", "ParentSnapshotName": "snap 2", "CreationTime": "/Date(1524072333067)/",
"ParentSnapshotId": "s2", "Id": "s3"},
{"Name": "snap 2", "ParentSnapshotName": "snap 1", "CreationTime": "/Date(1524072333067)/",
"ParentSnapshotId": "s1", "Id": "s2"},
{"Name": "snap 1", "ParentSnapshotName": null, "CreationTime": "/Date(1514490360800)/",
"ParentSnapshotId": null, "Id": "s1"},
{"Name": "snap 5", "ParentSnapshotName": "snap 1", "CreationTime": "/Date(1524072333067)/",
"ParentSnapshotId": "s1", "Id": "s5"},
{"Name": "snap 4", "ParentSnapshotName": null, "CreationTime": "/Date(1514490360800)/",
"ParentSnapshotId": null, "Id": "s4"}]
"""

snaps_tree = """-- Virtual Machine Snapshots --
Virtual Machine
 +-- snap 1 ({dt1})
 |   +-- snap 5* ({dt2})
 |   +-- snap 2 ({dt2})
 |       +-- snap 3 ({dt2})
 +-- snap 4 ({dt1})
""".format(dt1=datetime.fromtimestamp(1514490360.800).strftime("%d/%m/%Y %H:%M:%S"),
           dt2=datetime.fromtimestamp(1524072333.067).strftime("%d/%m/%Y %H:%M:%S"))
