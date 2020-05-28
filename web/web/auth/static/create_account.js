import React from 'react';
import * as action from './actions';
import { ListDivider } from '@rmwc/list';
import { TextField } from '@rmwc/textfield';
import { Typography } from '@rmwc/typography';
import { Card, CardPrimaryAction, CardActions, CardActionButton } from '@rmwc/card';

import '@rmwc/card/styles';
import '@rmwc/list/styles';
import '@rmwc/textfield/styles';
import '@rmwc/typography/styles';

class CreateAccount extends React.PureComponent {
    state = {
        username: "",
        password: "",
        firstName: "",
        lastName: ""
    }

    render() {
        return (
            <Card outlined>
                <Typography
                    use="subtitle1"
                    tag="div"
                    style={{ padding: '0.5rem 1rem' }}>
                    Create Account
                </Typography>

                <ListDivider />

                <CardPrimaryAction>
                    <div style={{ padding: '1rem' }}>
                        <Typography use="headline5" tag="div">
                            Email
                        </Typography>
                        <TextField placeholder="joe.smith@tess.com" />
                    </div>
                </CardPrimaryAction>

                <ListDivider />

                <CardPrimaryAction>
                    <div style={{ padding: '1rem' }}>
                        <Typography use="headline5" tag="div">
                            Password
                        </Typography>
                        <Typography use="body1" tag="p">
                            Your password must be at least 8 characters long
                        </Typography>
                        <TextField type="password" placeholder="" />
                    </div>
                </CardPrimaryAction>

                <ListDivider />

                <CardPrimaryAction>
                    <div style={{ padding: '1rem' }}>
                        <Typography use="headline5" tag="div">
                            First Name
                        </Typography>
                        <TextField placeholder="Your First Name" />
                    </div>
                </CardPrimaryAction>

                <ListDivider />

                <CardPrimaryAction>
                    <div style={{ padding: '1rem' }}>
                        <Typography use="headline5" tag="div">
                            Last Name
                        </Typography>
                        <TextField placeholder="Your Last Name" />
                    </div>
                </CardPrimaryAction>

                <ListDivider />

                <CardActions fullBleed>
                    <CardActionButton label=" Go Back" onClick={() => this.props.setCreateFlow(false)} />
                    <CardActionButton label=" Create Account" />
                </CardActions>
            </Card>
        );
    }
}

export default CreateAccount;