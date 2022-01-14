import React, { Component } from 'react';
import { Suggestions, History, KeyBoard } from "./components";


export default class App extends Component {
    state = {
        length: 5,
        history: [
            [
                {'char': 'a', 'status': 'correct'},
                {'char': 'p', 'status': 'correct'},
                {'char': 'l', 'status': 'present'},
                {'char': 'b', 'status': 'absent'},
                {'char': 'd', 'status': 'absent'},
            ],
            [
                {'char': 'b', 'status': 'absent'},
                {'char': 'c', 'status': 'absent'},
                {'char': 'l', 'status': 'present'},
                {'char': 'e', 'status': 'absent'},
                {'char': 'f', 'status': 'absent'},
            ],
        ],
    }

    constructor(props) {
        super(props);
    }

    acceptSuggestion = (word) => {
        this.setState((prevState, props) => ({
            history: [
                ...prevState.history,
                [...word].map(item => ({'char': item, 'status': 'absent'}))
            ],
        }));
    }

    render() {
        return (
            <div className="App">
                <header className="App-header">
                    Wordle Plug In
                </header>
                <Suggestions {...this.state} acceptSuggestion={this.acceptSuggestion} />
                <History {...this.state} />
                <KeyBoard {...this.state} />
            </div>
        );
    }
}
