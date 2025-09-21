# Smart-Sheet
An AI-powered, response-driven interview system that dynamically evaluates Microsoft Excel proficiency through case-based scenarios and adaptive questioning.

## Overview

This system revolutionizes Excel skills assessment by generating questions in real-time based on candidate responses, creating personalized learning paths and providing contextually relevant datasets for each scenario. Unlike traditional fixed-sequence assessments, this platform adapts to individual performance levels and focuses on areas that need the most attention.

## Key Features

### Adaptive Question Generation
- **Dynamic Question Creation**: Questions are generated in batches of 2 based on candidate performance
- **Response-Driven Trajectory**: Assessment path changes based on demonstrated capabilities
- **Real-Time Adaptation**: System adjusts difficulty and focus areas based on ongoing evaluation
- **Intelligent Progression**: Each question builds on previous responses and identified skill gaps

### Contextual Data Generation
- **Business-Realistic Datasets**: AI generates datasets that perfectly match question scenarios
- **Data Quality Challenges**: Includes realistic data issues (missing values, inconsistencies) for practice
- **Context-Aware Creation**: Datasets align with specific Excel challenges being tested
- **HTML Table Display**: Clean, professional presentation of generated data

### Performance Analysis
- **Candidate Profile Evolution**: Tracks strengths, weaknesses, and learning patterns
- **Trend Analysis**: Monitors performance improvement, decline, or stability
- **Skill Gap Identification**: Automatically identifies untested or weak skill areas
- **Difficulty Calibration**: Adjusts question complexity based on demonstrated ability

### Case-Based Assessment
- **Scenario-Driven Questions**: Realistic business situations requiring Excel solutions
- **Methodology Focus**: Tests Excel thinking and problem-solving approach
- **No Software Required**: Candidates explain their approach verbally
- **Progressive Complexity**: Questions advance based on individual capability

## System Architecture

### Core Components

#### 1. Adaptive Orchestrator (`AdaptiveInterviewOrchestrator`)
- **Purpose**: Main controller managing adaptive interview flow
- **Responsibilities**:
  - Candidate profile management
  - Dynamic question generation coordination
  - Performance trend analysis
  - Trajectory decision making
  - Assessment completion logic

#### 2. AI Agents

##### QueCraft Agent
- **Function**: Case-based question generation with contextual data
- **Capabilities**:
  - Scenario design based on business contexts
  - Dataset requirement specification
  - Question-data alignment validation
  - Adaptive reasoning integration

##### Reviewer Agent
- **Function**: Response evaluation and scoring
- **Capabilities**:
  - Excel methodology assessment
  - Problem-solving logic evaluation
  - Strengths and weaknesses identification
  - Follow-up question recommendations

##### Recruiter Agent
- **Function**: Final decision making and comprehensive assessment
- **Capabilities**:
  - Overall performance synthesis
  - Hiring recommendation generation
  - Skill competency rating
  - Development area identification

##### Interviewer Agent
- **Function**: Conversational interface management
- **Capabilities**:
  - Question presentation
  - Response acknowledgment
  - Clarification requests
  - Interview flow management

#### 3. Enhanced Data Generator (`MockDataGenerator`)
- **LLM Integration**: Uses AI to understand question context
- **Smart Data Creation**: Generates datasets that support specific Excel challenges
- **Quality Control**: Includes realistic data issues for comprehensive testing
- **Format Flexibility**: Outputs data in multiple formats (HTML, CSV, JSON)

### Technical Infrastructure

#### LLM Client Management
- **Dual Model Architecture**: 
  - Gemini Pro for complex reasoning tasks
  - Gemini Flash for conversational interactions
- **Rate Limiting**: Intelligent request management
- **Error Handling**: Comprehensive failure recovery
- **Performance Monitoring**: Real-time usage tracking

#### Tool Integration
- **Web Search**: Research Excel best practices and current information
- **Report Generation**: Comprehensive feedback and analysis reports
- **Tool Logging**: Detailed performance and usage analytics
- **JSON Processing**: Robust parsing and validation

## Assessment Process

### 1. Initialization Phase
```
Candidate Setup → Profile Creation → Initial Question Generation (2 questions)
```

### 2. Adaptive Assessment Loop
```
Present Question → Collect Response → Evaluate Performance → Update Profile → 
Generate Next Questions (if needed) → Continue or Complete
```

### 3. Decision Points
- **Continue Assessment**: Based on skill coverage and performance stability
- **Adjust Difficulty**: Increase/decrease complexity based on demonstrated ability
- **Focus Areas**: Target weak skills or explore untested domains
- **Complete Assessment**: When sufficient data collected or maximum questions reached

### 4. Results Generation
```
Performance Analysis → Skill Assessment → Trajectory Review → 
Personalized Feedback → Comprehensive Report
```

## Detailed Features

### Adaptive Intelligence
- **Profile Learning**: System builds detailed candidate profile during assessment
- **Trajectory Decisions**: Logged reasoning for each adaptive choice made
- **Performance Prediction**: Anticipates candidate capability in untested areas
- **Personalization Engine**: Tailors experience to individual learning patterns

### Excel Skills Coverage
- Basic Formulas and Functions
- Data Manipulation and Cleaning
- Lookup Functions (VLOOKUP, INDEX/MATCH)
- Pivot Tables and Data Analysis
- Data Visualization and Charts
- Conditional Logic and IF Statements
- Text Functions and String Manipulation
- Advanced Functions and Array Formulas
- Data Validation and Error Handling
- Macro Basics and Automation Concepts

### Business Scenarios
- Marketing Campaign Analysis
- Sales Performance Tracking
- Financial Reporting and Budgeting
- Inventory Management
- Employee Performance Metrics
- Customer Data Analysis
- Project Timeline Management
- Survey Data Processing

### Assessment Metrics
- **Overall Proficiency Score**: Comprehensive performance rating
- **Skill-Specific Assessment**: Individual area competency levels
- **Performance Trend**: Learning trajectory analysis
- **Adaptive Effectiveness**: Personalization success measurement
- **Question Efficiency**: Optimal assessment coverage analysis

## Technical Requirements

### Dependencies
```
streamlit>=1.29.0
google-generativeai>=0.3.0
pandas>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
faker>=20.0.0
logging>=0.4.9.6
datetime
json5>=0.9.0
typing-extensions>=4.8.0
faker>=20.0.0
google-genai>=1.38.0
```

### Environment Setup
1. Google API Key for Gemini models
2. Python 3.8+ environment
3. Streamlit web interface
4. Required Python packages

### Configuration
- **Model Selection**: Gemini 2.0 Flash for optimal performance
- **Rate Limiting**: Configurable API request limits
- **Assessment Parameters**: Customizable question counts and difficulty ranges
- **Data Generation**: Adjustable dataset sizes and complexity

## User Interface

### Streamlit Web Application
- **Responsive Design**: Works across different screen sizes
- **Professional Styling**: Clean, corporate-appropriate interface
- **Real-Time Updates**: Dynamic progress tracking and feedback
- **Interactive Elements**: Dataset viewers, progress indicators, performance charts

### Key UI Components
- **Candidate Setup**: Profile configuration and preferences
- **Chat Interface**: Conversational assessment experience
- **Dataset Viewer**: Contextual data exploration
- **Progress Tracking**: Real-time adaptive decisions and skill coverage
- **Results Dashboard**: Comprehensive performance analysis
- **Report Generation**: Downloadable feedback documents

## Deployment

### Local Development
```bash
# Clone repository
git clone [https://github.com/adityalakhani/Smart-Sheet](https://github.com/adityalakhani/Smart-Sheet)

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY=your_api_key

# Run application
streamlit run app.py
```

### Production Considerations
- **Scalability**: Horizontal scaling for multiple concurrent assessments
- **Security**: API key management and data protection
- **Monitoring**: Performance tracking and error logging
- **Backup**: Assessment data and configuration backup strategies

## Data Privacy and Security

### Data Handling
- **Minimal Storage**: Only assessment-relevant data retained
- **Secure Processing**: API communications encrypted
- **Privacy Compliance**: Follows data protection best practices
- **Temporary Data**: Generated datasets exist only during assessment

### Security Features
- **API Key Protection**: Environment variable configuration
- **Rate Limiting**: Prevents abuse and manages costs
- **Error Handling**: Graceful failure without data exposure
- **Audit Logging**: Comprehensive activity tracking

## Performance Optimization

### System Efficiency
- **Smart Caching**: Reduces redundant API calls
- **Batch Processing**: Optimizes question generation
- **Lazy Loading**: Datasets generated only when needed
- **Resource Management**: Efficient memory and API usage

### Assessment Optimization
- **Targeted Questioning**: Focuses on areas needing evaluation
- **Adaptive Stopping**: Completes when sufficient data collected
- **Skill Prioritization**: Tests critical areas first
- **Efficiency Metrics**: Tracks assessment effectiveness

## Future Enhancements

### Planned Features
- **Multi-Language Support**: Assessment in different languages
- **Advanced Analytics**: Machine learning-based insights
- **Integration APIs**: Connect with HR systems and LMS platforms
- **Mobile Optimization**: Enhanced mobile assessment experience
- **Collaborative Features**: Team assessment capabilities

### Technical Improvements
- **Performance Optimization**: Further response time improvements
- **Advanced AI Models**: Integration with newer language models
- **Enhanced Data Generation**: More sophisticated dataset creation
- **Expanded Skill Coverage**: Additional Microsoft Office applications

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request with detailed description

### Code Standards
- **PEP 8**: Python code formatting
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Detailed docstrings and comments
- **Testing**: Unit tests for core functionality

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For technical support, bug reports, or feature requests, please create an issue in the project repository with detailed information about your environment and the specific problem encountered.

## Acknowledgments

This project leverages several open-source libraries and tools:
- **Streamlit**: Web application framework
- **Google Gemini**: Large language model API
- **Pandas**: Data manipulation and analysis
- **Faker**: Realistic test data generation

---

Made with ❤ by Aditya Lakhani
