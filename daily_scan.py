import generate_candidates
import scan

print("Generating candidates...")
generate_candidates.generate()

print("Scanning today's best pick...")
scan.scan()

print("Completed daily scan!")
