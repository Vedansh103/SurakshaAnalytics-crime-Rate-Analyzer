from crime_analyzer import CrimeAnalyzer

def main():
    # Initialize analyzer
    analyzer = CrimeAnalyzer('districtwise-ipc-crimes-2017-onwards.csv')
    
    print("🔍 CRIME ANALYSIS SYSTEM")
    print("="*50)
    
    while True:
        # STEP 1: Select State
        print(f"\n📍 STEP 1: Select State")
        for i, state in enumerate(analyzer.states, 1):
            print(f"{i:2d}. {state}")
        
        state_input = input(f"\nEnter state number (or 'exit'): ").strip()
        
        if state_input.lower() == 'exit':
            break
            
        if not state_input.isdigit() or int(state_input) < 1 or int(state_input) > len(analyzer.states):
            print("Invalid selection!")
            continue
            
        selected_state = analyzer.states[int(state_input) - 1]
        print(f"✅ Selected: {selected_state}")
        
        # STEP 2: Select District/City
        districts = analyzer.get_districts_by_state(selected_state)
        print(f"\n🏘️ STEP 2: Select District/City in {selected_state}")
        
        for i, district in enumerate(districts, 1):
            print(f"{i:2d}. {district}")
        
        district_input = input(f"\nEnter district number: ").strip()
        
        if not district_input.isdigit() or int(district_input) < 1 or int(district_input) > len(districts):
            print("Invalid selection!")
            continue
            
        selected_district = districts[int(district_input) - 1]
        print(f"✅ Selected: {selected_district}")
        
        # STEP 3: Select Crime Type
        print(f"\n🚔 STEP 3: Select Crime Type")
        for i, crime in enumerate(analyzer.crime_columns, 1):
            print(f"{i:2d}. {crime.replace('_', ' ').title()}")
        
        crime_input = input(f"\nEnter crime number: ").strip()
        
        if not crime_input.isdigit() or int(crime_input) < 1 or int(crime_input) > len(analyzer.crime_columns):
            print("Invalid selection!")
            continue
            
        selected_crime = analyzer.crime_columns[int(crime_input) - 1]
        print(f"✅ Selected: {selected_crime.replace('_', ' ').title()}")
        
        # STEP 4: Select Graph Type
        print(f"\n📊 STEP 4: Select Graph Type")
        graph_options = [
            ("Line Chart", analyzer.line_chart),
            ("Bar Chart", analyzer.bar_chart),
            ("Interactive Chart", analyzer.interactive_chart),
            ("Pie Chart", analyzer.pie_chart),
            ("Area Chart", analyzer.area_chart)
        ]
        
        for i, (name, _) in enumerate(graph_options, 1):
            print(f"{i}. {name}")
        
        graph_input = input(f"\nEnter graph number: ").strip()
        
        if not graph_input.isdigit() or int(graph_input) < 1 or int(graph_input) > len(graph_options):
            print("Invalid selection!")
            continue
            
        selected_graph_name, selected_graph_func = graph_options[int(graph_input) - 1]
        print(f"✅ Selected: {selected_graph_name}")
        
        # Graph selection loop
        while True:
            # Generate Analysis
            print(f"\n🔍 Generating {selected_graph_name} for {selected_crime} in {selected_district}, {selected_state}...")
            selected_graph_func(selected_state, selected_district, selected_crime)
            
            # Ask for next action
            print(f"\nWhat would you like to do next?")
            print("1. Try another graph type for same data")
            print("2. Start new analysis (different state/city/crime)")
            print("3. Exit")
            
            next_choice = input(f"\nEnter your choice (1-3): ").strip()
            
            if next_choice == '1':
                # Show graph options again
                print(f"\n📊 Select Graph Type")
                for i, (name, _) in enumerate(graph_options, 1):
                    print(f"{i}. {name}")
                
                graph_input = input(f"\nEnter graph number: ").strip()
                
                if graph_input.isdigit() and 1 <= int(graph_input) <= len(graph_options):
                    selected_graph_name, selected_graph_func = graph_options[int(graph_input) - 1]
                    print(f"✅ Selected: {selected_graph_name}")
                else:
                    print("Invalid selection!")
                    continue
            elif next_choice == '2':
                break  # Break inner loop to start new analysis
            elif next_choice == '3':
                print(f"\nThank you for using Crime Analysis System! 🚔")
                return
            else:
                print("Invalid choice!")
                continue

if __name__ == "__main__":
    main()