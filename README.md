# 🏃 Apple Health Workout Parser & Visualizer

Parse Apple Health XML exports and visualize your workout data with interactive charts and statistics.

## 📊 Features

- **Parse Apple Health XML** - Converts Apple's complex XML export into clean, usable data
- **Extract Workout Data** - Pulls calories burned, duration, type, and timestamps
- **Generate CSV** - Creates an easy-to-use CSV file for further analysis
- **Interactive Visualization** - React-based web app with charts and statistics
- **Docker Support** - Containerized for easy deployment and consistency
- **Handle Large Files** - Efficiently processes multi-gigabyte XML files using streaming

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Apple iPhone with Health app data

### 1. Export Your Health Data from iPhone

1. Open **Health** app on iPhone
2. Tap your **Profile** (top right corner)
3. Tap the **Menu** (top right)
4. Select **Export Health Data**
5. Choose **Save to Files** and save to iCloud Drive
6. Download the ZIP file to your computer

### 2. Set Up the Project

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/apple-health-parser.git
cd apple-health-parser

# Create folders if they don't exist
mkdir -p data output
```

### 3. Prepare Your Data

1. Extract the ZIP file from iPhone
2. Find the `export.xml` file inside
3. Copy it to the `data/` folder:
   ```bash
   cp /path/to/export.xml data/
   ```

### 4. Run the Parser with Docker

```bash
# Build and run
docker-compose up --build
```

The parser will:
- Read your XML file
- Extract all workout data
- Generate `export_workouts.csv` in the `output/` folder
- Display statistics in the terminal

### 5. Check Your Results

```bash
# View the CSV file
head -20 output/export_workouts.csv

# See file size
ls -lh output/export_workouts.csv
```

## 📈 What You Get

### CSV Output

Your data is converted to a clean CSV file with columns:

```
Date,Time,Type,Duration (min),Calories (kcal),Source
2023-01-01,12:28:38,Walking,32,60,Apple Watch
2023-01-17,13:42:51,Walking,10,28,Apple Watch
2023-02-07,13:26:26,Walking,30,61,Apple Watch
```

### Statistics

The parser outputs detailed statistics:

```
✅ Success! Extracted 1447 workouts
📊 Statistics:
   • Total Workouts: 1447
   • Total Calories: 219,519 kcal
   • Average Calories: 152 kcal
   • Total Duration: 1070 hours
   • Workout Types:
     - Walking: 678 workouts, 76,995 kcal total, 114 kcal avg
     - Cycling: 290 workouts, 57,637 kcal total, 199 kcal avg
     - Mixed Cardio: 188 workouts, 37,775 kcal total, 201 kcal avg
     ...
```

## 🏗️ Project Structure

```
apple-health-parser/
├── .gitignore                      # Git ignore rules
├── .gitattributes                  # Line ending rules
├── .env.example                    # Environment variables template
├── .dockerignore                   # Docker build ignore rules
├── README.md                       # This file
├── Dockerfile                      # Docker container configuration
├── docker-compose.yml              # Docker compose orchestration
├── requirements.txt                # Python dependencies
├── parse_apple_health.py           # Main parser script
├── data/                           # Input folder (not in git)
│   └── export.xml                  # Your Apple Health export (place here)
└── output/                         # Output folder (not in git)
    └── export_workouts.csv         # Generated CSV file
```

## 🐳 Docker Setup

The project uses Docker for consistency and to avoid local Python setup issues.

### What Happens When You Run `docker-compose up --build`

1. **Builds** a Docker image with Python 3.11 and dependencies
2. **Mounts** your `data/` folder as `/app/data` in the container
3. **Mounts** your `output/` folder as `/app/output` in the container
4. **Runs** the parser script
5. **Creates** `export_workouts.csv` in your local `output/` folder

### Commands

```bash
# Run the parser
docker-compose up --build

# Run without rebuilding
docker-compose up

# Stop and clean up
docker-compose down

# View logs
docker-compose logs -f

# Remove all Docker artifacts
docker-compose down --volumes
docker image rm apple-health-parser-parser
```

## 📊 Supported Workout Types

The parser recognizes these Apple Health workout types:

- Walking
- Running
- Cycling
- Cardio
- HIIT (High Intensity Interval Training)
- Swimming
- Elliptical
- Yoga
- Pilates
- Strength Training
- Functional Strength
- Dance
- Mixed Cardio
- Stair Climbing
- Hiking
- And others!

## 🔒 Security & Privacy

- **Your data stays local** - The XML file is in `.gitignore` and never pushed to GitHub
- **Generated files are ignored** - CSV outputs are not committed
- **No credentials stored** - `.env` file is in `.gitignore`
- **Docker volumes are ephemeral** - No data persists in containers

## 🛠️ How It Works

### Step 1: XML Parsing

The parser uses Python's `xml.etree.ElementTree` to efficiently stream through your XML file without loading it all into memory. This allows it to handle multi-gigabyte files.

### Step 2: Data Extraction

For each `<Workout>` element, it extracts:
- **Workout type** - What kind of exercise (Running, Yoga, etc.)
- **Start/end dates** - When the workout happened
- **Duration** - How long it took
- **Calories** - From the `WorkoutStatistics` child element
- **Source** - Which device recorded it

### Step 3: Data Transformation

- Converts Apple's workout type codes to readable names
- Parses timestamps into date and time components
- Handles unit conversions (kJ to kcal, hours to minutes, etc.)
- Filters out incomplete workouts (no calories recorded)

### Step 4: CSV Export

Data is sorted by date and written to a clean CSV file that you can:
- Open in Excel
- Analyze with Python/Pandas
- Upload to the visualization web app
- Share with others

## 🚧 Future Features

- [ ] Web app for visualization and filtering
- [ ] Database integration (PostgreSQL)
- [ ] Real-time streaming from HealthKit
- [ ] Advanced analytics and trends
- [ ] Export to multiple formats
- [ ] API for programmatic access

## 🐛 Troubleshooting

### "No space left on device"

Docker doesn't have enough space. Check Docker desktop settings or clean up:

```bash
docker system prune -a
```

### "No workouts found"

Your XML file may not have the expected structure. Check:

```bash
grep -i "WorkoutStatistics" data/export.xml | head -3
```

Should show `<WorkoutStatistics>` elements with energy data.

### CSV is empty or has wrong data

Check if the file was parsed correctly:

```bash
wc -l output/export_workouts.csv
head -20 output/export_workouts.csv
```

### Docker volume issues

Ensure your paths are correct:

```bash
ls -la data/
ls -la output/
```

## 📖 Further Learning

### About Apple Health Export

- [Apple Health Support](https://support.apple.com/en-us/HT211200)
- [HealthKit Documentation](https://developer.apple.com/healthkit/)

### Python & Docker Resources

- [Python XML Parsing](https://docs.python.org/3/library/xml.etree.elementtree.html)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Guide](https://docs.docker.com/compose/)

## 🤝 Contributing

Feel free to:
- Report issues
- Suggest improvements
- Add more workout type mappings
- Improve documentation

## 📄 License

MIT License - Feel free to use this for personal or commercial projects

## 🙋 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Verify your XML file has the correct structure
4. Check that file paths are correct

## 📝 Changelog

### Version 1.0.0 (Initial Release)
- ✅ XML parser with streaming support
- ✅ Workout type mapping
- ✅ CSV export
- ✅ Docker containerization
- ✅ Statistics and reporting

---

**Made with ❤️ for tracking your fitness journey**