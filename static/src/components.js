import React, { Component } from 'react';
import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';

export function Suggestions() {
    return (
        <div style={{margin: "50px auto", fontSize: "20px"}}>
            <span> their </span>
            <span> could </span>
        </div>
    );
}

export function History() {
    return (
        <div className="board">
            <div className="tile correct-button">D</div>
            <div className="tile correct-button">T</div>
            <div className="tile correct-button">D</div>
            <div className="tile present-button">T</div>
            <div className="tile present-button">T</div>

            <div className="tile present-button">D</div>
            <div className="tile present-button">T</div>
            <div className="tile absent-button">D</div>
            <div className="tile absent-button">T</div>
            <div className="tile absent-button">T</div>

            <div className="tile present-button">D</div>
            <div className="tile present-button">T</div>
            <div className="tile absent-button">D</div>
            <div className="tile absent-button">T</div>
            <div className="tile absent-button">T</div>

            <div className="tile present-button">D</div>
            <div className="tile present-button">T</div>
            <div className="tile absent-button">D</div>
            <div className="tile absent-button">T</div>
            <div className="tile absent-button">T</div>

            <div className="tile present-button">D</div>
            <div className="tile present-button">T</div>
            <div className="tile absent-button">D</div>
            <div className="tile absent-button">T</div>
            <div className="tile absent-button">T</div>
        </div>
    );
}

export class KeyBoard extends Component {
    onChange = (input) => {
        console.log("Input changed", input);
    }

    onKeyPress = (button) => {
        console.log("Button pressed", button);
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
                        buttons: "Q W E R T Y"
                    },
                    {
                        class: "absent-button",
                        buttons: "Z X C V"
                    }
                ]}
            />
        );
    }
}
