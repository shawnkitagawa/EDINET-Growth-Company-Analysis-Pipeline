#!/bin/bash
set -e

echo "Step 1-2: Running Python EDINET pipeline..."
python main.py

echo "Step 3: Running dbt models..."
cd edinet_dbt
dbt run --profiles-dir .
dbt test --profiles-dir .
cd ..

echo "Step 4: Exporting dbt outputs..."
python -m scripts.step4_visualization.export_dbt_outputs

echo "Step 4: Creating visualizations..."
python -m scripts.step4_visualization.create_visualizations

echo "Pipeline completed successfully."