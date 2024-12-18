import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFacePipeline
from smells import getAllSmellsInASingleString
from typing import List, Optional
from pydantic import BaseModel, Field

load_dotenv()

hugging_face_api_key = os.getenv("HUGGING_FACE_API_KEY")

# class DetectedSmell(BaseModel):
#     smellName: str
#     reason: str
    
class DetectedSmells(BaseModel):
    smellNames: List[str] = Field(description="List of detected smells")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash-8b",
#     api_key="",
# )

llm = HuggingFaceEndpoint(
    repo_id="MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF",
    task="text-generation",    
    temperature=0.01,
    huggingfacehub_api_token=hugging_face_api_key,
)

# llm = HuggingFacePipeline.from_model_id(
#     model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
#     task="text-generation",
#     pipeline_kwargs={"max_new_tokens": 512}    
# )

# structured_llm = llm.with_structured_output(DetectedSmells)

all_smells = getAllSmellsInASingleString()

def detectSmell(test_code: str, production_code: str) -> list[str]:        

    message = [
        SystemMessage(
            "You are an expert in detecting test smells. You will be given a test code block and a production code block. You have to identify which smells the test code contains. The test block may contain multiple smells, single smell or no smells at all. Here is the list of test smells: " + all_smells
        ),
        HumanMessage("Here is the test code block:" + test_code + "Here is the production code block:" + production_code + "Tell the name of the test smell(s) the test code block contains"),
    ]
    
    # print(message)

    response = llm.invoke(message)    
    # print(response)

    # explanation_instructions = [
    #     SystemMessage(
    #         "You are a expert in explaining smells in test code. You will be given a test code block and a production code block. You have to explain why the test code block contains certain test smells. Here is the list of test smells: " + all_smells
    #     ),
    #     HumanMessage("Here is the test code block:" + test_code + "Here is the production code block:" + production_code + "Can you explain why the test code block contains the following smells : " + str(response.smellNames)),
    # ]

    # response = llm.invoke(explanation_instructions)
    # print(response)
    
    return response

if __name__ == "__main__":
    test_code = """
    @Test
    public void realCase() {
        Point p34 = new Point("34", 556506.667, 172513.91, 620.34, true);
        Point p45 = new Point("45", 556495.16, 172493.912, 623.37, true);
        Point p47 = new Point("47", 556612.21, 172489.274, 0.0, true);
        Abriss a = new Abriss(p34, false);
        a.removeDAO(CalculationsDataSource.getInstance());
        a.getMeasures().add(new Measure(p45, 0.0, 91.6892, 23.277, 1.63));
        a.getMeasures().add(new Measure(p47, 281.3521, 100.0471, 108.384, 1.63));

        try {
            a.compute();
        } catch (CalculationException e) {
            Assert.fail(e.getMessage());
        }

        // test intermediate values with point 45
        Assert.assertEquals("233.2405",
            this.df4.format(a.getResults().get(0).getUnknownOrientation()));
        Assert.assertEquals("233.2435",
            this.df4.format(a.getResults().get(0).getOrientedDirection()));
        Assert.assertEquals("-0.1", this.df1.format(
            a.getResults().get(0).getErrTrans()));

        // test intermediate values with point 47
        Assert.assertEquals("233.2466",
            this.df4.format(a.getResults().get(1).getUnknownOrientation()));
        Assert.assertEquals("114.5956",
            this.df4.format(a.getResults().get(1).getOrientedDirection()));
        Assert.assertEquals("0.5", this.df1.format(
            a.getResults().get(1).getErrTrans()));

        // test final results
        Assert.assertEquals("233.2435", this.df4.format(a.getMean()));
        Assert.assertEquals("43", this.df0.format(a.getMSE()));
        Assert.assertEquals("30", this.df0.format(a.getMeanErrComp()));
    }
    """
    production_code = "not available"

    res = detectSmell(test_code, production_code)
    
    print(res)
    print(type(res))