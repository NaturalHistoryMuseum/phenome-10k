# Upload multiple files to phenome10k

To make uploads faster, zip the individual files. Assuming source files are in `src`:

```bash
./zip.sh src
```

 Requires records.json to contain array of objects like this:
 ```json
 {
    "scientific name": "Salamandra salamandra gigliolii",
    "alt name (optional)": "",
    "source filename": "Salamandra_salamandra_gigliolii_BMNH_1852.12.11.64",
    "specimen id (optional)": "BMNH_1852.12.11.64",
    "specimen location (optional)": "Natural History Museum, UK",
    "specimen url (optional)": "",
    "description": "",
    "geologic age": "extant",
    "ontogenetic age": "adult",
    "elements": "cranium",
    "gbif backbone id (if known)": ""
  }
```

This can be done with

```bash
./records.js src.csv
```
