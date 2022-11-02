import {getProjectParametersURL, getProjectTestPlans, getProjectTestSuitesURL} from "../api";
import axios from "axios";

export const SHOW_ADD_EDIT_TEST_PLAN_MODAL = 'SHOW_ADD_EDIT_TEST_PLAN_MODAL'
export const HIDE_ADD_EDIT_TEST_PLAN_MODAL = 'HIDE_ADD_EDIT_TEST_PLAN_MODAL'

export const showAddEditTestPlanModal = (isEditMode = false) => {
    return {
        type: SHOW_ADD_EDIT_TEST_PLAN_MODAL,
        isEditMode: isEditMode
    }
}

export const hideAddEditTestPlanModal = () => {
    return {
        type: HIDE_ADD_EDIT_TEST_PLAN_MODAL
    }
}

export const FETCH_TEST_PLANS_PENDING = 'FETCH_TEST_PLANS_PENDING'
export const FETCH_TEST_PLANS_ERROR = 'FETCH_TEST_PLANS_ERROR'
export const FETCH_TEST_PLANS_SUCCESS = 'FETCH_TEST_PLANS_SUCCESS'

export const fetchTestPlansPending = () => {
    return {
        type: FETCH_TEST_PLANS_PENDING
    }
}

export const fetchTestPlansError = (error) => {
    return {
        type: FETCH_TEST_PLANS_ERROR,
        error: error
    }
}

export const fetchTestPlansSuccess = (payload) => {
    return {
        type: FETCH_TEST_PLANS_SUCCESS,
        payload: payload
    }
}

export const fetchTestPlans = () => {
    return dispatch => {
        dispatch(fetchTestPlansPending())

        axios.get(
            getProjectTestPlans(PROJECT_ID),
        ).then(response => {
            dispatch(fetchTestPlansSuccess(response.data))
        }).catch(thrown => {
            console.log('Error fetch test plans', thrown)
            dispatch(fetchTestPlansError(thrown))
        });
    }
}

export const FETCH_TEST_SUITES_PENDING = 'FETCH_TEST_SUITES_PENDING'
export const FETCH_TEST_SUITES_ERROR = 'FETCH_TEST_SUITES_ERROR'
export const FETCH_TEST_SUITES_SUCCESS = 'FETCH_TEST_SUITES_SUCCESS'

export const fetchTestSuitesPending = () => {
    return {
        type: FETCH_TEST_SUITES_PENDING
    }
}

export const fetchTestSuitesError = (error) => {
    return {
        type: FETCH_TEST_SUITES_ERROR,
        error: error
    }
}

export const fetchTestSuitesSuccess = (payload) => {
    return {
        type: FETCH_TEST_SUITES_SUCCESS,
        payload: payload
    }
}

export const fetchTestSuites = () => {
    return dispatch => {
        dispatch(fetchTestSuitesPending())

        axios.get(
            getProjectTestSuitesURL(PROJECT_ID),
        ).then(response => {
            dispatch(fetchTestSuitesSuccess(response.data))
        }).catch(thrown => {
            console.log('Error fetch test suites', thrown)
            dispatch(fetchTestSuitesError(thrown))
        });
    }
}


export const FETCH_PARAMETERS_PENDING = 'FETCH_PARAMETERS_PENDING'
export const FETCH_PARAMETERS_ERROR = 'FETCH_PARAMETERS_ERROR'
export const FETCH_PARAMETERS_SUCCESS = 'FETCH_PARAMETERS_SUCCESS'

export const fetchParametersPending = () => {
    return {
        type: FETCH_PARAMETERS_PENDING
    }
}

export const fetchParametersError = (error) => {
    return {
        type: FETCH_PARAMETERS_ERROR,
        error: error
    }
}

export const fetchParametersSuccess = (payload) => {
    return {
        type: FETCH_PARAMETERS_SUCCESS,
        payload: payload
    }
}

export const fetchParameters = () => {
    return dispatch => {
        dispatch(fetchParametersPending())

        axios.get(
            getProjectParametersURL(PROJECT_ID),
        ).then(response => {
            dispatch(fetchParametersSuccess(response.data))
        }).catch(thrown => {
            console.log('Error fetch parameters', thrown)
            dispatch(fetchParametersError(thrown))
        });
    }
}