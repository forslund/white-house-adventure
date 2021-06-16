Feature: Zork

  Scenario: Start game
    Given an english speaking user
     When the user says "go to the white house"
     Then mycroft reply should contain "white house"

  Scenario: Leave game
    Given an english speaking user
     When the user says "quit"
     Then "game-zork" should reply with dialog from "LeavingZork.dialog"
