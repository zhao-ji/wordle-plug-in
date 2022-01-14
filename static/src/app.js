import React, { Component } from 'react';
import { Suggestions, History, KeyBoard } from "./components";


export default class App extends Component {
    state = {
        length: 5,
        history: [],
        input: [],
    }

    acceptSuggestion = (word) => {
        this.setState((prevState, props) => ({
            history: [
                ...prevState.history,
                [...word].map(item => ({'char': item, 'status': 'absent'}))
            ],
        }));
    }

    onTileFlip = (wordIndex, characterIndex, characterStatus) => {
        const statusSwitch = {
            "absent": "present",
            "present": "correct",
            "correct": "absent",
        };
        this.setState((prevState, props) => {
            const oldHistory = JSON.parse(JSON.stringify(prevState.history));
            oldHistory[wordIndex][characterIndex].status = statusSwitch[characterStatus];
            return { history: oldHistory };
        });
    }

    onWordRemove = (wordIndex) => {
        this.setState((prevState, props) => {
            const oldHistory = JSON.parse(JSON.stringify(prevState.history));
            oldHistory.splice(wordIndex, 1);
            return { history: oldHistory };
        });
    }

    onInputUpdate = (text) => {
        this.setState((prevState, props) => ({
            input: [...prevState.input, text],
        }));
    }

    onInputBackSpace = () => {
        if (!this.state.input.length) return;
        this.setState((prevState, props) => {
            const newInput = prevState.input.slice(0, prevState.input.length - 1);
            return {input: newInput};
        });
    }

    onInputConfirm = () => {
        this.setState((prevState, props) => ({
            history: [
                ...prevState.history,
                prevState.input.map(item => ({'char': item, 'status': 'absent'}))
            ],
            input: [],
        }));
    }

    render() {
        return (
            <div className="App">
                <header className="App-header">
                    Wordle Plug In
                </header>
                <Suggestions
                    acceptSuggestion={this.acceptSuggestion}
                    {...this.state}
                />
                <History
                    onTileFlip={this.onTileFlip}
                    onWordRemove={this.onWordRemove}
                    input={this.state.input}
                    {...this.state}
                />
                <KeyBoard
                    onInputUpdate={this.onInputUpdate}
                    onInputConfirm={this.onInputConfirm}
                    onInputBackSpace={this.onInputBackSpace}
                    {...this.state}
                />
            </div>
        );
    }
}
