import React, { Component } from 'react';

import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';


export async function fetchSuggestions({ length, history }) {
    const body = { length, history };
    let url = new URL("https://plug-in.minganci.org/api/");

    const response = await fetch(url, {
        method: 'post',
        headers: {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body),
    });
    const data = await response.json();
    return data;
}


export class Suggestions extends Component {
    state = {
        suggestions: [],
    }

    componentDidMount() {
        this.updateSuggestions();
    }

    componentDidUpdate(prevProps) {
        const {length, history} = prevProps;
        const {length: _length, history: _history} = this.props;
        if (length !== _length || history.length !== _history.length) {
            this.updateSuggestions();
        }
    }

    updateSuggestions() {
        fetchSuggestions(this.props).then(result => {
            this.setState({ suggestions: result, });
        });
    }

    onSuggestionClick(suggestions) {
        this.props.acceptSuggestion(suggestions);
        // this.props.setHistory([
        //     ...this.props.history,
        //     [...suggestions].map(item => ({
        //         'char': item.toUpperCase(),
        //         'status': 'absent',
        //     }))
        // ]);
    }

    render() {
        if (this.state.suggestions.length === 0) return ("");
        return (
            <div id="suggestions">
                {this.state.suggestions.map(suggestion => (
                    <button
                        key={suggestion}
                        className="suggest-button"
                        onClick={() => this.props.acceptSuggestion(suggestion)}
                    >
                        {suggestion}
                    </button>
                ))}
            </div>
        );
    }
}

export class History extends Component {
    render() {
        const gridTemplateColumns = `repeat(${this.props.length + 1}, 1fr)`;
        return (
            <div className="board" style={{gridTemplateColumns,}}>
                {this.props.history.map(word => (
                    <>
                        {word.map(character => (
                            <div className={`tile ${character.status}-button`}>
                                {character.char}
                            </div>
                        ))}
                        <button className="suggest-button">
                            Action
                        </button>
                    </>
                ))}
            </div>
        );
    }
}

export class KeyBoard extends Component {
    onChange = (input) => {
        console.log("Input changed", input);
    }

    onKeyPress = (button) => {
        console.log("Button pressed", button);
    }

    getCorrectButtons = () => {
        return [].concat.apply([], this.props.history).filter(
            item => item.status === "correct"
        ).map(item => item.char).join(" ").toUpperCase();
    }

    getPresentButtons = () => {
        return [].concat.apply([], this.props.history).filter(
            item => item.status === "present"
        ).map(item => item.char).join(" ").toUpperCase();
    }

    getAbsentButtons = () => {
        return [].concat.apply([], this.props.history).filter(
            item => item.status === "absent"
        ).map(item => item.char).join(" ").toUpperCase();
    }

    render() {
        return (
            <Keyboard
                onChange={this.onChange}
                onKeyPress={this.onKeyPress}
                layout={{
                    default: [
                        'Q W E R T Y U I O P',
                        'A S D F G H J K L',
                        '{enter} Z X C V B N M {bksp}',
                    ],
                }}
                display={{
                    "{bksp}": "⌫",
                    "{enter}": "RETURN",
                }}
                buttonTheme={[
                    {
                        class: "correct-button",
                        buttons: this.getCorrectButtons()
                    },
                    {
                        class: "present-button",
                        buttons: this.getPresentButtons()
                    },
                    {
                        class: "absent-button",
                        buttons: this.getAbsentButtons()
                    }
                ]}
            />
        );
    }
}
