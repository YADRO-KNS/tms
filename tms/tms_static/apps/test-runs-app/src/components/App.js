import React from "react";
import {Provider} from "react-redux";
import TestPlanActions from "./TestPlanActions";
import TestPlanContent from "./TestPlanContent";
import AddEditTestPlanModal from "./AddEditTestPlanModal";

const App = ({store}) => {
    return (
        <Provider store={store}>
            <div className="p-4">
                <TestPlanActions/>
                <div className=" p-3 bg-white">
                    <TestPlanContent/>
                </div>
            </div>
            <AddEditTestPlanModal/>
        </Provider>
    )
}

export default App