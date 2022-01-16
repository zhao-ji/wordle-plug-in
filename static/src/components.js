import React, { Component } from 'react';

import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';


export async function fetchSuggestions({ length, history }) {
    const body = { length, history };
    const url = new URL("https://plug-in.minganci.org/api/history/");

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


export function Length ({ length, onLengthChange }) {
    const lengthLimit = 15;
    const lengthRange = Array.from(Array(lengthLimit).keys()).map(i => i + 1);
    return (
        <span className="length-section">
            <label style={{display: "inline-block"}}>Length:</label>
            <select
                style={{display: "inline-block"}}
                id="length"
                name="length"
                value={length}
                onChange={onLengthChange}
            >
                {lengthRange.map(item => (
                    <option value={item}>
                        {item}
                    </option>
                ))}
            </select>
        </span>
    );
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
        if (length !== _length || JSON.stringify(history) !== JSON.stringify(_history)) {
            this.updateSuggestions();
        }
    }

    updateSuggestions() {
        fetchSuggestions(this.props).then(result => {
            this.setState({ suggestions: result, });
        });
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

const Tile = ({ character, wordIndex, characterIndex, onTileFlip }) => {
    return (
        <button
            className={`tile ${character.status}-button suggest-button`}
            onClick={() => onTileFlip(wordIndex, characterIndex, character.status)}
        >
            {character.char}
        </button>
    );
}

export function History ({ length, history, onTileFlip, onWordRemove, input}) {
    const gridTemplateColumns = `repeat(${length + 1}, 1fr)`;
    const gridTemplateRows = `repeat(${history.length + 1}, 1fr)`;
    return (
        <div className="board" style={{gridTemplateColumns, gridTemplateRows}}>
            {history.map((word, wordIndex) => (
                <>
                    {word.map((character, characterIndex) => (
                        <Tile
                            key={wordIndex * 100 + characterIndex}
                            character={character}
                            wordIndex={wordIndex}
                            characterIndex={characterIndex}
                            onTileFlip={onTileFlip}
                        />
                    ))}
                    <button
                        className="suggest-button"
                        onClick={() => onWordRemove(wordIndex)}
                    >
                        ⌫
                    </button>
                </>
            ))}
            {[...Array(length)].map((_, index) => (
                <button className="tile suggest-input-button" key={index}>
                    {input.length > index ? input[index] : '\u00a0\u00a0'}
                </button>
            ))}
        </div>
    );
}

export class KeyBoard extends Component {
    onKeyPress = (button) => {
        if (button === '{enter}') {
            if (this.props.input.length === this.props.length)
                this.props.onInputConfirm();
        } else if (button === '{bksp}') {
            this.props.onInputBackSpace();
        } else {
            if (this.props.input.length < this.props.length)
                this.props.onInputUpdate(button.toLowerCase());
        }
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
                    "{enter}": "ENTER",
                }}
                buttonTheme={[
                    {
                        class: "absent-button",
                        buttons: this.getAbsentButtons()
                    },
                    {
                        class: "present-button",
                        buttons: this.getPresentButtons()
                    },
                    {
                        class: "correct-button",
                        buttons: this.getCorrectButtons()
                    },
                ]}
            />
        );
    }
}
