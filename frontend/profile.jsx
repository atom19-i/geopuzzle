'use strict';
import React from "react";
import {render} from "react-dom";
import Profile from "./profile/index";
import messages from "./locale/messages";
import {IntlProvider} from "react-intl";


let node = document.getElementById('profile');

render(
    <IntlProvider locale={window.__LANGUAGE__} messages={messages[window.__LANGUAGE__]}>
      <Profile user={window.__USER__} providers={window.__PROVIDERS__}/>
    </IntlProvider>, node);
