# Excel parser for cobrapy
_Author: Nirvana Nursimulu_

The code in this repository is meant to parse an Excel file describing a constraint-based metabolic model, that can then be manipulated via cobrapy.  The Excel file follows the same format as those that can be loaded via cobratoolbox (example is "sample_model.xlsx").

Usage: 

```
import Excel_reader as er
model = er.get_cobrapy_model(path_to_excel_file)
````
