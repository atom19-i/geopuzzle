'use strict';
import React from "react";
import {render} from "react-dom";
import Puzzle from "./games/Puzzle";
import Quiz from "./games/Quiz";
import messages from "./locale/messages";
import {IntlProvider} from "react-intl";

let games = {
  'puzzle': <Puzzle map={window.__MAP__} game={window.__GAME__}/>,
  'quiz': <Quiz map={window.__MAP__} game={window.__GAME__} options={window.__OPTIONS__}/>,
};


for (let [game, component] of Object.entries(games)) {
  let node = document.getElementById(game);
  if (node !== null) {
      render(
        <IntlProvider locale={window.__LANGUAGE__} messages={messages[window.__LANGUAGE__]}>
          {component}
        </IntlProvider>, node);
  }
}
