/**
 * Copyright (c) 2015-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 *  
 * Extending Button class for TESS (SLAC) 
 */

'use strict'

import React from 'react'
import { Text, View, Platform, StyleSheet, TouchableOpacity, TouchableNativeFeedback } from 'react-native'

const PropTypes = require('prop-types')
const invariant = require('fbjs/lib/invariant')


/**
 * A basic button component that should render nicely on any platform. Supports
 * a minimal level of customization.
 *
 * <center><img src="img/buttonExample.png"></img></center>
 *
 * If this button doesn't look right for your app, you can build your own
 * button using [TouchableOpacity](docs/touchableopacity.html)
 * or [TouchableNativeFeedback](docs/touchablenativefeedback.html).
 * For inspiration, look at the [source code for this button component](https://github.com/facebook/react-native/blob/master/Libraries/Components/Button.js).
 * Or, take a look at the [wide variety of button components built by the community](https://js.coach/react-native?search=button).
 *
 * Example usage:
 *
 * ```
 * import { Button } from 'react-native';
 * ...
 *
 * <Button
 *   onPress={onPressLearnMore}
 *   title="Learn More"
 *   color="#841584"
 *   accessibilityLabel="Learn more about this purple button"
 * />
 * ```
 *
 */

class Button extends React.Component {    
    render() {
        const { accessibilityLabel, borderColor, textColor, color, onPress, title, hasTVPreferredFocus, disabled, testID, borderRadius, width, isSecondary } = this.props
        const buttonStyles = [styles.button]
        const textStyles = [styles.text]
        
        if(color) {
            buttonStyles.push({backgroundColor: color})
        }

        if(borderColor) {
            buttonStyles.push({borderColor: borderColor})
        }

        // explicit null and undefined comparison because borderRadius can be 0, which evals to false
        if(borderRadius !== null && borderRadius !== undefined) {
            buttonStyles.push({borderRadius}) 
        }

        if(width !== null && width !== undefined) {
            buttonStyles.push({width})
        }

        if(textColor) {
            textStyles.push({color: textColor})
        }

        const accessibilityTraits = ['button']

        if(isSecondary) {
            buttonStyles.push(styles.buttonSecondary)
            textStyles.push(styles.textSecondary)
        }
        
        if(disabled) {
            buttonStyles.push(styles.buttonDisabled)
            textStyles.push(styles.textDisabled)
            accessibilityTraits.push('disabled')
        }
        
        invariant(typeof title === 'string', 'The title prop of a Button must be a string',)
        
        const formattedTitle = Platform.OS === 'android' ? title.toUpperCase() : title
        const Touchable = Platform.OS === 'android' ? TouchableNativeFeedback : TouchableOpacity

        return (<Touchable 
                    accessibilityComponentType="button"
                    accessibilityLabel={accessibilityLabel}
                    accessibilityTraits={accessibilityTraits}
                    hasTVPreferredFocus={hasTVPreferredFocus}
                    testID={testID}
                    disabled={disabled}
                    onPress={onPress}
                    style={buttonStyles}>
                    <View style={buttonStyles}>
                        <Text style={textStyles} disabled={disabled}>
                            {formattedTitle}
                        </Text>
                    </View>
                </Touchable>
        )
    }
}

const styles = StyleSheet.create({
    button: Platform.select({
        ios: {
            borderWidth: 1,
            backgroundColor: '#FFF',
            borderColor: '#000',
            borderRadius: 2,
        },
        android: {
            elevation: 4,
            // Material design blue from https://material.google.com/style/color.html#color-color-palette
            backgroundColor: '#FFF',
            borderColor: '#000',
            borderRadius: 2
        },
    }),
    buttonSecondary: Platform.select({
        ios: {
            borderWidth: .5,
            backgroundColor: '#FFFFFF',
            borderColor: '#CBCBCB',
            borderRadius: 3,
        },
        android: {
            borderWidth: .5,
            elevation: 4,
            // Material design blue from https://material.google.com/style/color.html#color-color-palette
            backgroundColor: '#FFFFFF',
            borderColor: '#CBCBCB',
            borderRadius: 3
        },
    }),
    text: Platform.select({
        ios: {
            // iOS blue from https://developer.apple.com/ios/human-interface-guidelines/visual-design/color/
            color: '#202020',
            textAlign: 'center',
            padding: 12,
            fontSize: 18,
        },
        android: {
            color: '#202020',
            textAlign: 'center',
            padding: 12,
            fontWeight: '400',
            fontFamily: 'Roboto'
        },
    }),
    textSecondary: Platform.select({
        ios: {
            // iOS blue from https://developer.apple.com/ios/human-interface-guidelines/visual-design/color/
            color: '#474747',
            textAlign: 'center',
            padding: 12,
            letterSpacing: 1,
            fontSize: 14,
            lineHeight: 19,
            fontWeight: '500',
            fontFamily: 'Roboto'
        },
        android: {
            color: '#474747',
            fontSize: 14,
            textAlign: 'center',
            padding: 12,
            letterSpacing: 1,
            lineHeight: 19,
            fontWeight: '500',
            fontFamily: 'Roboto'
        },
    }),
    buttonDisabled: Platform.select({
        ios: {
            backgroundColor: '#dfdfdf',
            borderColor: '#dfdfdf'
        },
        android: {
            elevation: 0,
            backgroundColor: '#dfdfdf',
        },
    }),
    textDisabled: Platform.select({
        ios: {
            color: '#a1a1a1',
        },
        android: {
            color: '#a1a1a1',
        },
    }),
});

module.exports = Button