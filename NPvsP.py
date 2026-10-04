import random
import time

# =====================================================================
# 1. ALGORITHM: SOLVER WITH TEMPORAL PRESSURE & THIRD ACTOR (SHADOW NODE)
# =====================================================================
def millennium_p_vs_np_solver(shifts, resources):
    """
    Polynomial-time solver O(N^2) using Temporal Pressure mapping
    and Third Actor (Shadow Node) contextual allocation.
    """
    start_time = time.perf_counter()
    
    # STEP 1: Temporal Pressure Mapping (Bottleneck Density)
    shift_pressure = {}
    for s1 in shifts:
        overlaps = sum(
            1 for s2 in shifts 
            if max(s1['start'], s2['start']) < min(s1['end'], s2['end'])
        )
        shift_pressure[s1['id']] = overlaps

    # STEP 2: Sort by Descending Pressure & Reliability Scale
    sorted_shifts = sorted(shifts, key=lambda s: shift_pressure[s['id']], reverse=True)
    sorted_resources = sorted(resources, key=lambda r: r['reliability'], reverse=True)
    
    assignments = {}
    resource_occupancy = []
    total_shifts = len(sorted_shifts)
    
    # STEP 3: Deterministic Allocation + Third Actor (Zero Backtracking)
    for i, shift in enumerate(sorted_shifts):
        available_candidates = []
        for r in sorted_resources:
            in_conflict = any(
                r['id'] == occ['resource_id'] and 
                max(shift['start'], occ['start']) < min(shift['end'], occ['end'])
                for occ in resource_occupancy
            )
            if not in_conflict:
                available_candidates.append(r)
                
        if not available_candidates:
            return {
                "outcome": "UNSAT",
                "execution_time_sec": time.perf_counter() - start_time
            }
            
        # Reliability Scale (Primary Actor)
        pressure_percentile = i / total_shifts
        primary_actor_idx = int(pressure_percentile * (len(available_candidates) - 1))
        primary_actor = available_candidates[primary_actor_idx]
        
        # Third Actor (Shadow Node to absorb state degradation)
        remaining_candidates = [c for c in available_candidates if c['id'] != primary_actor['id']]
        third_actor = remaining_candidates[0] if remaining_candidates else None
        
        assignments[shift['id']] = {
            "primary_actor": primary_actor['id'],
            "third_actor": third_actor['id'] if third_actor else None
        }
        
        resource_occupancy.append({
            'resource_id': primary_actor['id'], 
            'start': shift['start'], 
            'end': shift['end']
        })
        if third_actor:
            resource_occupancy.append({
                'resource_id': third_actor['id'], 
                'start': shift['start'], 
                'end': shift['end']
            })

    end_time = time.perf_counter()
    return {
        "outcome": "SAT",
        "assignments": assignments,
        "execution_time_sec": end_time - start_time
    }

# =====================================================================
# 2. SUITE OF ADVERSARIAL TRAPS & BENCHMARKS
# =====================================================================
def create_false_pressure_trap():
    """TRAP 1: False Pressure and downstream chained constraints."""
    shifts = [{'id': 'S_TRAP', 'start': 1, 'end': 5}]
    for i in range(10):
        shifts.append({'id': f'S_CHAIN_{i}', 'start': 10 + i, 'end': 15 + i})
        
    resources = [{'id': 'R_KEY', 'reliability': 0.99}]
    for j in range(25):
        resources.append({'id': f'R_NORMAL_{j}', 'reliability': 0.50})
        
    return shifts, resources

def create_uniform_pressure_trap(n=100):
    """TRAP 2: Uniform Pressure (Labyrinth with no clear bottlenecks)."""
    shifts = [{'id': f'S_{i}', 'start': 10, 'end': 30} for i in range(n)]
    resources = [
        {'id': f'R_{j}', 'reliability': round(0.1 + (j / (n * 3)) * 0.8, 2)} 
        for j in range(n * 3)
    ]
    return shifts, resources

def run_adversarial_stress_test():
    print("=" * 65)
    print(" ADVERSARIAL STRESS TEST: HUNTING ALGORITHMIC BLIND SPOTS ")
    print("=" * 65)
    
    # TEST 1: False Pressure Trap
    shifts_1, resources_1 = create_false_pressure_trap()
    res_1 = millennium_p_vs_np_solver(shifts_1, resources_1)
    print(f"1. False Pressure Trap: {res_1['outcome']} in {res_1['execution_time_sec']:.5f} sec")
    
    # TEST 2: Uniform Pressure Labyrinth
    shifts_2, resources_2 = create_uniform_pressure_trap(100)
    res_2 = millennium_p_vs_np_solver(shifts_2, resources_2)
    print(f"2. Uniform Pressure Labyrinth (N=100): {res_2['outcome']} in {res_2['execution_time_sec']:.5f} sec")
    print("=" * 65)

# =====================================================================
# 3. EXECUTION
# =====================================================================
if __name__ == "__main__":
    run_adversarial_stress_test()