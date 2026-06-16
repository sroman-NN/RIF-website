# RIF-WEBSITE

Minimal website for share releases,DOCS and more about the project originally created by : <a href="https://github.com/GrandKenzy">GrandKenzy</a>

> what is rif ? (Summary)

rif or retargable ISA Foundry is a retargable ISA generator, that is, a toolchain or framework ideal for creating ISAs on different architectures more easily.

> release process

1.drop release.zip in `releases`
2.edit manifest.json an add the release file,version,date and devlog(optional)
example manifest.json struct:
```
{
    "releases": [
        "zip_file_name | v1.0 | 15/6/2026 19:33 GMT-4",
        "rar_file_name | v1.2 | 00/0/0000 00:00 GMT-4",
        "tar_file_name | v1.3 | 00/0/0000 00:00 GMT-4",
        "ar1_file_name | v1.4 | 00/0/0000 00:00 GMT-4"
        
    ]
}
```