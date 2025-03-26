#!/bin/bash
# run_batch.sh
# This script runs bad_scanner.py with nested loops over several parameters:
#   - --blur-radius: 0, 1, 2, 3, 4
#   - --dust-density: 0, 1.25, 2.5, 3.75, 5.0
#   - --scratch-count: 0, 2, 5, 7, 10
#
# The remaining parameters are fixed at extreme values:
#   --dust-min-radius 5 --dust-max-radius 15 --dust-alpha-min 150 --dust-alpha-max 255
#   --scratch-line-width-min 2 --scratch-line-width-max 5 --scratch-alpha-min 150 --scratch-alpha-max 255
#
# Each output PDF is saved in the 'scans' directory as scanned_XXX.pdf,
# and the command used to generate each scan is recorded in scans/scan_commands.txt.
#
# Usage: ./run_batch.sh input.pdf

# Check for input file parameter
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 input_pdf"
  exit 1
fi

input="$1"

# Create the output directory if it doesn't exist
mkdir -p scans

# Create (or overwrite) the commands log file
commands_file="scans/scan_commands.txt"
> "$commands_file"

# Define arrays for the parameters we want to vary
blur_radius_vals=(0 1 2 3 4)
dust_density_vals=(0 1.25 2.5 3.75 5.0)
scratch_count_vals=(0 2 5 7 10)

# Counter for sequential output filenames (e.g., scanned_001.pdf, scanned_002.pdf, etc.)
i=1

# Nested loops over the parameter arrays
for blur in "${blur_radius_vals[@]}"; do
  for dust in "${dust_density_vals[@]}"; do
    for scratch in "${scratch_count_vals[@]}"; do
      
      # Format the output file name
      output=$(printf "scans/scanned_%03d.pdf" "$i")
      
      # Build the command string
      cmd="python bad_scanner.py \"$input\" \"$output\" --blur-radius $blur --dust-density $dust --dust-min-radius 5 --dust-max-radius 15 --dust-alpha-min 150 --dust-alpha-max 255 --scratch-count $scratch --scratch-line-width-min 2 --scratch-line-width-max 5 --scratch-alpha-min 150 --scratch-alpha-max 255"
      
      # Log and print the command
      echo "Running: $cmd"
      echo "$cmd" >> "$commands_file"
      
      # Execute the command
      eval $cmd
      
      # Increment the counter
      i=$((i + 1))
    done
  done
done

echo "Batch processing complete. Total scans: $((i-1))."
echo "See '$commands_file' for the list of commands used."

