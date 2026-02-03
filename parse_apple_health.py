#!/usr/bin/env python3
"""
Parse Apple Health XML export and extract workout data to CSV
Handles large files efficiently with streaming
"""

import xml.etree.ElementTree as ET
import csv
import sys
from pathlib import Path

# Mapping of Apple workout types to readable names
WORKOUT_TYPE_MAP = {
    'HKWorkoutActivityTypeYoga': 'Yoga',
    'HKWorkoutActivityTypeDanceInspiredCardio': 'Dance',
    'HKWorkoutActivityTypeTraditionalStrengthTraining': 'Strength',
    'HKWorkoutActivityTypeCycling': 'Cycling',
    'HKWorkoutActivityTypeHighIntensityIntervalTraining': 'HIIT',
    'HKWorkoutActivityTypeCardio': 'Cardio',
    'HKWorkoutActivityTypePilates': 'Pilates',
    'HKWorkoutActivityTypeRunning': 'Running',
    'HKWorkoutActivityTypeWalking': 'Walking',
    'HKWorkoutActivityTypeSwimming': 'Swimming',
    'HKWorkoutActivityTypeElliptical': 'Elliptical',
    'HKWorkoutActivityTypeStairs': 'Stairs',
    'HKWorkoutActivityTypeCoreTraining': 'Core',
    'HKWorkoutActivityTypeFunctionalStrengthTraining': 'Functional Strength',
    'HKWorkoutActivityTypeOther': 'Other',
}

def parse_duration(duration_str, duration_unit):
    """Convert duration to minutes"""
    if not duration_str or not duration_unit:
        return 0
    try:
        duration = float(duration_str)
        if duration_unit == 'min':
            return int(duration)
        elif duration_unit == 'sec':
            return int(duration / 60)
        elif duration_unit == 'hr':
            return int(duration * 60)
        return int(duration)
    except:
        return 0

def parse_energy(energy_str, energy_unit):
    """Convert energy to kcal"""
    if not energy_str:
        return 0
    try:
        energy = float(energy_str)
        # Apple typically uses kcal or kJ
        if energy_unit == 'kJ':
            return int(energy / 4.184)  # Convert kJ to kcal
        return int(energy)
    except:
        return 0

def extract_date(datetime_str):
    """Extract just the date from datetime string"""
    if not datetime_str:
        return ''
    try:
        # Format: "2024-01-15 10:30:45 +0000"
        return datetime_str.split(' ')[0]
    except:
        return datetime_str

def extract_time(datetime_str):
    """Extract just the time from datetime string"""
    if not datetime_str:
        return ''
    try:
        # Format: "2024-01-15 10:30:45 +0000"
        parts = datetime_str.split(' ')
        if len(parts) >= 2:
            return parts[1]
        return ''
    except:
        return ''

def main():
    # Get input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = 'export.xml'

    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Error: File '{input_file}' not found")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir = Path('/app/output')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / (input_path.stem + '_workouts.csv')

    print(f"📊 Parsing Apple Health XML...")
    print(f"📁 Input: {input_file}")
    print(f"💾 Output: {output_file}")
    print(f"⏳ This may take a few minutes for large files...\n")

    workouts = []
    error_count = 0

    try:
        # Parse XML with iterative parsing to handle large files
        context = ET.iterparse(input_file, events=('end',))

        for event, elem in context:
            if elem.tag == 'Workout':
                try:
                    # Extract workout-level attributes
                    activity_type = elem.get('workoutActivityType', 'Unknown')
                    duration = elem.get('duration', '0')
                    duration_unit = elem.get('durationUnit', 'min')
                    start_date = elem.get('startDate', '')
                    end_date = elem.get('endDate', '')
                    source = elem.get('sourceName', 'Unknown')

                    # Parse duration
                    duration_min = parse_duration(duration, duration_unit)

                    # Extract energy from WorkoutStatistics child element
                    calories = 0
                    for stat in elem.findall('WorkoutStatistics'):
                        stat_type = stat.get('type', '')
                        if stat_type == 'HKQuantityTypeIdentifierActiveEnergyBurned':
                            energy_sum = stat.get('sum', '0')
                            energy_unit = stat.get('unit', 'kcal')
                            calories = parse_energy(energy_sum, energy_unit)
                            break  # Found the energy, stop looking

                    # Extract date and time
                    date = extract_date(start_date)
                    time = extract_time(start_date)

                    # Only include workouts with calories data and valid dates
                    if calories > 0 and date:
                        workout_type = WORKOUT_TYPE_MAP.get(activity_type, activity_type)

                        workouts.append({
                            'Date': date,
                            'Time': time,
                            'Type': workout_type,
                            'Duration (min)': duration_min,
                            'Calories (kcal)': calories,
                            'Source': source,
                            'Raw Type': activity_type
                        })

                        if len(workouts) % 100 == 0:
                            print(f"✓ Processed {len(workouts)} workouts...")

                    # Clear element to free memory
                    elem.clear()

                except Exception as e:
                    error_count += 1
                    if error_count < 10:  # Only print first few errors
                        print(f"⚠️  Error parsing workout: {e}")

    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

    if not workouts:
        print("❌ No workouts found in the XML file")
        print("⚠️  Make sure your export.xml contains Workout elements with HKQuantityTypeIdentifierActiveEnergyBurned statistics")
        sys.exit(1)

    # Sort by date
    workouts.sort(key=lambda x: x['Date'])

    # Write to CSV
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Date', 'Time', 'Type', 'Duration (min)', 'Calories (kcal)', 'Source']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for workout in workouts:
                row = {k: workout[k] for k in fieldnames}
                writer.writerow(row)

        print(f"\n✅ Success! Extracted {len(workouts)} workouts")
        print(f"📊 Statistics:")

        # Calculate stats
        total_calories = sum(w['Calories (kcal)'] for w in workouts)
        total_duration = sum(w['Duration (min)'] for w in workouts)
        avg_calories = total_calories / len(workouts)

        print(f"   • Total Workouts: {len(workouts)}")
        print(f"   • Total Calories: {total_calories:,} kcal")
        print(f"   • Average Calories: {avg_calories:.0f} kcal")
        print(f"   • Total Duration: {total_duration:,} minutes ({total_duration//60} hours)")

        # Workout type breakdown
        type_counts = {}
        type_calories = {}
        for w in workouts:
            wtype = w['Type']
            type_counts[wtype] = type_counts.get(wtype, 0) + 1
            type_calories[wtype] = type_calories.get(wtype, 0) + w['Calories (kcal)']

        print(f"   • Workout Types:")
        for wtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            total_cal = type_calories[wtype]
            avg_cal = total_cal / count
            print(f"     - {wtype}: {count} workouts, {total_cal:,} kcal total, {avg_cal:.0f} kcal avg")

        print(f"\n💾 File saved: {output_file}")
        print(f"📤 You can now upload this CSV to the web app!")

    except Exception as e:
        print(f"❌ Error writing CSV: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()