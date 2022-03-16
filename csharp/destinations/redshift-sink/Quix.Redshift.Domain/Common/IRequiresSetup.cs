using System.Threading.Tasks;

namespace Quix.Redshift.Domain.Common
{
    public interface IRequiresSetup
    {
        Task Setup();
    }
}