# Bet Slip Logic

This document outlines the high-level logic for core bet slip functionalities in a sports betting application.

## 1. User Selecting an Odd

*   **Description:**
    A user browses available matches and their associated odds. When a user finds an outcome they want to bet on (e.g., "Team A to win"), they click on the displayed odd value. This action signifies their intent to add this specific bet to their bet slip.

*   **Information Captured:**
    When an odd is selected, the system should capture at least the following information:
    *   `odd_id`: The unique identifier for the selected odd.
    *   `match_id`: The unique identifier for the match this odd belongs to.
    *   `market_name`: The name of the market (e.g., "Match Winner", "Total Goals Over/Under 2.5").
    *   `outcome`: The specific outcome selected by the user (e.g., "Team A", "Over 2.5").
    *   `value`: The decimal value of the odd at the time of selection.
    *   `team1_name`, `team2_name` (or similar identifiers for the match participants).
    *   `start_time` of the match.

    ```pseudocode
    FUNCTION on_user_select_odd(selected_odd_details):
        // selected_odd_details contains: odd_id, match_id, market_name, outcome, value, team1_name, team2_name, start_time
        captured_selection = {
            "odd_id": selected_odd_details.odd_id,
            "match_id": selected_odd_details.match_id,
            "market_name": selected_odd_details.market_name,
            "outcome": selected_odd_details.outcome,
            "odd_value": selected_odd_details.value,
            "match_participants": selected_odd_details.team1_name + " vs " + selected_odd_details.team2_name,
            "match_start_time": selected_odd_details.start_time,
            "stake": 0.0, // Initialize stake
            "potential_winnings": 0.0 // Initialize potential winnings
        }
        add_to_bet_slip(captured_selection)
    ```

## 2. Adding Selection to Bet Slip

*   **Description:**
    The bet slip acts as a temporary container for selections the user is considering betting on.

*   **Data Structure:**
    The bet slip can be represented as a list of objects (or dictionaries), where each object corresponds to a selected odd and its associated betting information.
    ```pseudocode
    GLOBAL bet_slip_selections = [] // List to store selected odds
    ```

*   **Adding a New Selection:**
    When a user selects an odd, the captured information (as an object/dictionary) is added to the `bet_slip_selections` list.
    ```pseudocode
    FUNCTION add_to_bet_slip(selection_data):
        existing_selection_index = find_selection_in_slip(selection_data.odd_id)

        IF existing_selection_index IS NOT -1: // Odd is already in the slip
            remove_from_bet_slip(existing_selection_index) // Remove it
        ELSE:
            bet_slip_selections.append(selection_data)
        
        update_bet_slip_display()
    
    FUNCTION find_selection_in_slip(odd_id_to_find):
        FOR index, selection IN enumerate(bet_slip_selections):
            IF selection.odd_id == odd_id_to_find:
                RETURN index
        RETURN -1 // Not found

    FUNCTION remove_from_bet_slip(selection_index):
        bet_slip_selections.pop(selection_index)
        update_bet_slip_display() // And recalculate totals
    ```
    *Self-correction: The prompt specified that "selecting an already selected odd removes it". The above pseudocode for `add_to_bet_slip` reflects this.*

*   **Bet Slip Display (Conceptual):**
    The bet slip would typically be displayed as a separate panel or section on the UI. Each selection would be listed with:
    *   Match details (e.g., "Team A vs Team B").
    *   Market and outcome (e.g., "Match Winner: Team A").
    *   The odd value.
    *   An input field for the stake.
    *   Calculated potential winnings for that selection.
    *   A way to remove the selection from the slip.

## 3. User Inputting Stake

*   **Description:**
    For each individual selection in the bet slip, the user needs to be able to input the amount of money they wish to wager (the stake).

*   **Individual Stake Input:**
    Each item in the `bet_slip_selections` list (representing a selected odd) should have a property, say `stake`, which is updated when the user inputs a value in the corresponding stake input field on the UI.
    ```pseudocode
    FUNCTION on_user_input_stake(odd_id, new_stake_amount):
        selection_index = find_selection_in_slip(odd_id)
        IF selection_index IS NOT -1:
            bet_slip_selections[selection_index].stake = new_stake_amount
            calculate_potential_winnings_for_selection(odd_id) // Recalculate for this selection
            update_bet_slip_summary() // Update overall totals
            update_bet_slip_display_for_selection(odd_id) // Refresh UI for this selection
    ```

*   **Combination/Accumulator Bets (Future Consideration):**
    For combination bets (parlays/accumulators), users would typically input a single stake that applies to the combined odds of all selections. The logic would involve:
    *   Identifying if the user wants to place single bets or a combination bet.
    *   If combination, a separate input field for the accumulator stake.
    *   The calculation of combined odds would be `odd1_value * odd2_value * ... * oddN_value`.
    *   Potential winnings would then be `accumulator_stake * combined_odds`.
    *   This often means disabling individual stake inputs if an accumulator option is chosen.

## 4. Calculating Potential Winnings

*   **Description:**
    The system must calculate and display the potential winnings for each bet based on the stake and the odd value.

*   **Pseudocode for Single Bet:**
    ```pseudocode
    FUNCTION calculate_potential_winnings_for_selection(odd_id):
        selection_index = find_selection_in_slip(odd_id)
        IF selection_index IS NOT -1:
            selection = bet_slip_selections[selection_index]
            IF selection.stake > 0 AND selection.odd_value > 0:
                selection.potential_winnings = selection.stake * selection.odd_value
            ELSE:
                selection.potential_winnings = 0.0
            RETURN selection.potential_winnings
        RETURN 0.0 
    ```

*   **Updating on Change:**
    This calculation (`calculate_potential_winnings_for_selection`) should be triggered whenever:
    *   The stake for a selection is changed by the user.
    *   An odd is added to or removed from the bet slip (though for additions, stake is initially 0).
    *   (Important, but more advanced): If an odd's value changes *before* the bet is placed, the bet slip should ideally reflect this, and potential winnings recalculated. This requires real-time updates of odds. For now, we assume the odd value is fixed at the time of selection.

*   **Displaying Individual Potential Winnings:**
    Each selection listed in the bet slip UI should have its `potential_winnings` displayed next to it.

## 5. Bet Slip Summary

*   **Description:**
    A summary section provides the user with an overview of their current selections and potential outcomes if they were to place bets on all items currently in the slip as single bets.

*   **Useful Summary Information:**
    *   **Total Number of Selections:** The count of items in `bet_slip_selections`.
    *   **Total Stake (for Single Bets):** The sum of all `stake` amounts for individual selections in the bet slip.
    *   **Total Potential Winnings (for Single Bets):** The sum of all `potential_winnings` for individual selections.

    ```pseudocode
    FUNCTION get_bet_slip_summary():
        total_stake = 0.0
        total_potential_winnings = 0.0
        number_of_selections = len(bet_slip_selections)

        FOR selection IN bet_slip_selections:
            total_stake += selection.stake
            // Ensure potential winnings are calculated if stake is present but winnings are not yet set
            IF selection.stake > 0 AND selection.potential_winnings == 0.0:
                 calculate_potential_winnings_for_selection(selection.odd_id)
            total_potential_winnings += selection.potential_winnings
        
        RETURN {
            "number_of_selections": number_of_selections,
            "total_stake": total_stake,
            "total_potential_winnings": total_potential_winnings
        }

    FUNCTION update_bet_slip_summary():
        summary_data = get_bet_slip_summary()
        display_summary_in_ui(summary_data) // Update UI elements for total stake, total winnings etc.
    ```

This document provides a foundational outline. Further details would be needed for error handling (e.g., invalid stake input), bet placement confirmation, handling of voided bets, and more complex bet types.
