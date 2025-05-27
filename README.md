# Customer Support Agent

## Features

- **Product Recommendations**: Provides personalized product suggestions based on customer preferences using RAG (Retrieval Augmented Generation)
- **Order Status Lookup**: Retrieves order information using customer email and order number
- **Promotion Eligibility Check**: Verifies if customers qualify for the Early Risers Promotion (8-10 AM PT)

## Getting Started

### Prerequisites

1. Python 3.12 or higher
2. OpenAI API key

### Setup

1. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   
   Make sure your OpenAI API has the following models enabled:
   - **GPT-4o**: Used for conversational responses and function calling
   - **text-embedding-3-small**: Used for RAG-based product recommendations

4. Navigate to the `src` directory and run the application:
   ```
   cd src
   python support_agent_cli.py
   ```

## Architecture

![Architecture Diagram](Architecture.drawio.svg)

The Sierra Outfitters Customer Support Agent uses a modular architecture:

1. **SupportAgentServer**: This is the entry point of the application, managing the command-line interface (CLI) and handling user inputs.

2. **SupportAgent**: Acts as the core processing unit that processes user messages, dispatches function tools, and coordinates responses.

3. **LLMChatSession**: Responsible for managing interactions with the OpenAI API. 

4. **FunctionTools**: This module manages the execution of various tools that the system can utilize. 

   - **Recommend Product**: Uses retrieval-augmented generation (RAG) to provide contextually relevant product recommendations.
   - **Lookup Order**: Retrieves order information based on user queries.
   - **Check Promotion Eligibility**: Evaluates user eligibility for promotions based on current time.

5. **Data Stores**: These are repositories that store product and order information in memory and pre-process product catalog to genereate embedding.


## 🧠 Major Technical Decisions

### AI Usage

#### Agentic Workflows
I initially built each customer-facing workflow (e.g., order lookup, product recommendation) as a **separate, explicit flow** using intent detection. Each workflow was manually triggered and executed in sequential steps. While this was easy to prototype, I quickly ran into two limitations:

- **Inflexibility**: The assistant couldn't answer questions that is not implemented in workflow.
- **Latency**: Responses required repeated checks and control logic, slowing down interaction speed.

**Decision**: I transitioned to an **agentic tool-based workflow** where the assistant autonomously determines the next action. This improved natural flow, reduced response time, and made the agent feel more conversational and intelligent.

#### Few-Shot Prompting
By including example phrases in the system prompt, the model better understands user intent and response in a consistent brand tone.

#### Chain of Thought
For ambiguous or incomplete user inputs in workflow (e.g., order lookup), I encouraged reasoning with prompts that guide the model to:
1. Check if all required info is available (e.g., email or order number)
2. Ask for missing info (instead of asking both email and order number again)
3. Then call the correct function

### 🔍 RAG for Product Recommendations

I implemented a simple Retrieval-Augmented Generation (RAG) to solve the problem of recommending relevant products from a large catalog.

#### Problem:
- Evaluating all products in the prompt could potentially exceed token limits, especially in real life the product catalog will be significantly larger than the ProductCatalog.json example.
- It's expensive and slow to load the full catalog into GPT-4o

#### Solution:
- Precompute embeddings using `text-embedding-3-small`
- Retrieve top-K relevant products based on user preferences
- Post-evaluate top-K by using LLM to filter relavant product

**Trade-off**: While this adds a preprocessing step, it reduces latency and token consumption.

---

## 🚀 Things to Improve

### Vector Databases
Currently, product embeddings are stored in memory and searched with linear methods.

**Improvement Goal**: 
Replace this with a proper **vector database** like Pinecone, which will give us the following benifits.
- Faster and more scalable similarity search
- Native support for filtering (e.g., by tags, price range, category)
- Handles larger catalogs with dynamic updates

**Trade-off**: Adds infra complexity, but enables real-time retrieval at scale.

---

### Tool-Calling Optimizations

The current system performs tool calls one at a time with basic input checking.

**Improvement Goals**:
- Support parallel/sequential tool execution where applicable (e.g., user want us to search order and make recommendations at the same time)
- Add schema validation for stricter input/output checking

---

### Extensibility in Developing Function Tools

While the current `FunctionTool` class supports easy registration, scaling to more tools and team contributors could benefit from an SDK-based architecture.

**Improvement Options**:
- Adopt OpenAI's OpenAI Agents SDK or use Sierra Agent SDK
- Use decorators or auto-discovery to register new tools with metadata
- Add unit testing templates for new tool onboarding

---

### Stronger Context for Product Recommendation

Current recommendations are based solely on a single query + embedding.

**Improvement Ideas**:
- Incorporate **purchase history** to personalize results
- Use **behavioral signals** (e.g., recently viewed items)

---

### Evaluation Framework

A comprehensive evaluation system should measure:

| Criterion                | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| Tool Correctness         | Was the right function called with the correct parameters?                 |
| Task Completion          | Did the agent fulfill the user’s intent?                                   |
| Brand Tone Consistency   | Were responses friendly, concise, and adventure-themed?                    |
| Fallback Behavior        | Did the agent handle incomplete or missing data gracefully?                |

- Tools like DeepEval or LangSmith for evaluation
- User feedback surveys during real deployments

---

