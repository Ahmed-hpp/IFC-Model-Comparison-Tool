# IFC Model Comparison Tool (Software Lab - TUM)

This project is  **IFC Model Comparison and Diffing Tool** developed as part of the **Software Lab** course at the **Technical University of Munich (TUM)**, offered by the **Chair of Computational Modeling and Simulation (Prof. Dr.-Ing. André Borrmann)**.

The tool enables Architects and engineers to track changes between two versions of an IFC file, identifying added, deleted, and modified elements with high precision.

## 🚀 Features

The tool classifies modifications into three distinct categories:
* **Semantic Check**: Detects changes in attributes, Property Sets (PSets), and Quantity Sets (QSets) using graph-based comparisons.
* **Geometric Check**: Analyzes high-level geometric properties such as volume, surface area, centroids, and bounding boxes.
* **Shape Check**: Performs detailed 3D mesh comparison using **Hausdorff Distance** and grid-based sampling to detect subtle shape deviations.

## 📊 Reporting & Visualization

* **CSV Reports**: Generates detailed lists of added, deleted, and modified elements.
* **JSON/Text Logs**: Provides a deep dive into exactly what property changed (e.g., "Wall height changed from 3.0m to 3.2m").
* **3D Visualization**: Exports color-coded `.glb` files for 3D inspection:
    * 🟩 **Green**: Added Elements
    * 🟥 **Red**: Deleted Elements
    * 🟦 **Blue**: Modified Elements

## 🛠️ Installation & Setup


Ensure you download the required libraries listed in  requirements.txt

